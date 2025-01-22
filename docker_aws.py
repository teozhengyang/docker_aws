import os
import subprocess
import sys
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def get_user_input(prompt):
    """Get input from the user."""
    try:
        return input(prompt).strip()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
        sys.exit(1)

def run_command(command):
    """Run shell command and handle exceptions."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}\n{e.stderr}")
        sys.exit(1)

def login_to_ecr(aws_region, aws_account_id):
    """Authenticate Docker to AWS ECR."""
    try:
        print("Logging in to Amazon ECR...")
        ecr_login_command = f"aws ecr get-login-password --region {aws_region} | docker login --username AWS --password-stdin {aws_account_id}.dkr.ecr.{aws_region}.amazonaws.com"
        run_command(ecr_login_command)
    except (NoCredentialsError, PartialCredentialsError):
        print("AWS credentials not found or incomplete.")
        sys.exit(1)

def build_docker_image(dockerfile_path, app_path, repository_name, image_tag):
    """Build the Docker image."""
    print("Building Docker image...")
    run_command(f"docker build -t {repository_name}:{image_tag} -f {dockerfile_path} {app_path}")

def tag_docker_image(aws_account_id, aws_region, repository_name, image_tag):
    """Tag the Docker image for ECR."""
    print("Tagging Docker image...")
    ecr_image_tag = f"{aws_account_id}.dkr.ecr.{aws_region}.amazonaws.com/{repository_name}:{image_tag}"
    run_command(f"docker tag {repository_name}:{image_tag} {ecr_image_tag}")
    return ecr_image_tag

def push_docker_image(image_tag):
    """Push the Docker image to ECR."""
    print("Pushing Docker image to ECR...")
    run_command(f"docker push {image_tag}")

def main():
    try:
        # Get user inputs
        aws_region = get_user_input("Enter AWS region (e.g., us-east-1): ")
        aws_account_id = get_user_input("Enter AWS account ID: ")
        repository_name = get_user_input("Enter ECR repository name: ")
        image_tag = get_user_input("Enter Docker image tag (default: latest): ") or "latest"
        app_path = get_user_input("Enter path to your application directory (default: ./app): ") or "./app"
        dockerfile_path = get_user_input("Enter path to your Dockerfile (default: ./Dockerfile): ") or "./Dockerfile"

        # Execute deployment steps
        login_to_ecr(aws_region, aws_account_id)
        build_docker_image(dockerfile_path, app_path, repository_name, image_tag)
        ecr_image_tag = tag_docker_image(aws_account_id, aws_region, repository_name, image_tag)
        push_docker_image(ecr_image_tag)

        print("Docker image successfully pushed to AWS ECR!")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
