import subprocess
import json
import asyncio
import logging
from apify import Actor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Limit concurrency to avoid getting blocked or overwhelming the system
MAX_CONCURRENCY = 10
semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

async def check_email(target_email, from_email, hello_name, check_gravatar, hibp_api_key):
    async with semaphore:
        logger.info(f"Checking email: {target_email}")
        
        # Prepare command
        # Note: reacher-cli expects values for its boolean flags due to parse(try_from_str)
        cmd = [
            "reacher-cli",
            "--from-email", from_email,
            "--hello-name", hello_name,
            "--check-gravatar", "true" if check_gravatar else "false",
        ]
        
        if hibp_api_key:
            cmd.extend(["--haveibeenpwned-api-key", hibp_api_key])
            
        cmd.append(target_email)
        
        try:
            # Run the Rust binary with a timeout (e.g., 45 seconds per email)
            # Headless checks (Yahoo/Outlook) can take 20-30 seconds.
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=45.0)
                
                if process.returncode == 0:
                    try:
                        output_json = json.loads(stdout.decode().strip())
                        # Push result to dataset immediately
                        await Actor.push_data(output_json)
                        return output_json
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON for {target_email}: {e}")
                        logger.error(f"Output was: {stdout.decode()}")
                else:
                    logger.error(f"Rust binary failed for {target_email} with return code {process.returncode}")
                    logger.error(f"Stderr: {stderr.decode()}")
            except asyncio.TimeoutError:
                logger.error(f"Timeout reached while checking {target_email}. Killing process.")
                try:
                    process.kill()
                    await process.wait()
                except:
                    pass
        except Exception as e:
            logger.error(f"An error occurred while checking {target_email}: {e}")
    return None

async def main():
    async with Actor:
        # Get input
        actor_input = await Actor.get_input() or {}
        
        email = actor_input.get("email")
        emails = actor_input.get("emails", [])
        
        # Combine single email and list of emails
        to_check = []
        if email:
            to_check.append(email)
        if emails:
            to_check.extend(emails)
            
        if not to_check:
            status_message = "No emails provided in input. Please provide 'email' or 'emails' in the input JSON."
            logger.error(status_message)
            await Actor.exit(exit_code=1, status_message=status_message)
            return

        # Optional configuration from input
        from_email = actor_input.get("from_email", "reacher.email@gmail.com")
        hello_name = actor_input.get("hello_name", "gmail.com")
        check_gravatar = actor_input.get("check_gravatar", False)
        hibp_api_key = actor_input.get("haveibeenpwned_api_key")
        
        logger.info(f"Starting check for {len(to_check)} emails with concurrency {MAX_CONCURRENCY}.")

        # Run checks in parallel
        tasks = [
            check_email(target_email, from_email, hello_name, check_gravatar, hibp_api_key)
            for target_email in to_check
        ]
        
        results = await asyncio.gather(*tasks)
        valid_results = [r for r in results if r is not None]

        logger.info(f"Finished checking {len(to_check)} emails. {len(valid_results)} results pushed.")

if __name__ == "__main__":
    asyncio.run(main())
