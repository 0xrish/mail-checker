import subprocess
import json
import asyncio
import logging
from apify import Actor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        
        logger.info(f"Starting check for {len(to_check)} emails.")

        results = []
        for target_email in to_check:
            logger.info(f"Checking email: {target_email}")
            
            # Prepare command
            cmd = [
                "reacher-cli",
                "--from-email", from_email,
                "--hello-name", hello_name,
            ]
            
            if check_gravatar:
                cmd.append("--check-gravatar")
                
            cmd.append(target_email)
            
            try:
                # Run the Rust binary
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    try:
                        output_json = json.loads(stdout.decode().strip())
                        results.append(output_json)
                        # Push result to dataset immediately
                        await Actor.push_data(output_json)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON for {target_email}: {e}")
                        logger.error(f"Output was: {stdout.decode()}")
                else:
                    logger.error(f"Rust binary failed for {target_email} with return code {process.returncode}")
                    logger.error(f"Stderr: {stderr.decode()}")
                    
            except Exception as e:
                logger.error(f"An error occurred while checking {target_email}: {e}")

        logger.info(f"Finished checking {len(to_check)} emails. {len(results)} results pushed.")

if __name__ == "__main__":
    asyncio.run(main())
