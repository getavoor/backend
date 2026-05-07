"""
Planbot+
Setup script
(c) 2023-2025 githubcatw
"""

# Required for creating the config.js and .env files
import os
# Import an argument parser
import argparse

# Prefix of environment variables that should be saved.
PREFIX = "AVR_"

"""
Generates a .env file from the variables set when it's run.
A prefix check is used to only write the important variables to the .env file.
"""
def gen_dotenv():
    print("Generating .env file from the current environment...")
    # Open the env file.
    with open(".env", "w") as dotenv:
        # For every variable:
        for var in os.environ:
            # If the variable's name starts with our prefix, write it to the .env file.
            if var.startswith(PREFIX):
                dotenv.write(var + "=" + os.environ[var])
                # Write a new line too.
                dotenv.write("\n")
                # Print the name of the variable to the log.
                # Normally sensitive variables shouldn't be printed, however just writing the names is OK, especially if
                # the setup guide already lists the names.
                print("Written '" + var)

            # Some build environments require variables starting with underscores; accept those too.
            if var.startswith("_" + PREFIX):
                # However, in this case, the underscore has to be removed.
                # For this the first character from the name is removed.
                dotenv.write(var[1:] + "=" + os.environ[var])
                # Write a new line too.
                dotenv.write("\n")
                # Print the name of the variable to the log.
                # Normally sensitive variables shouldn't be printed, however just writing the names is OK, especially if
                # the setup guide already lists the names.
                print("Written " + var + " (without underscore)")

    print(".env file generated successfully!")


"""
The main setup function.
"""
def setup(args):
    # If creation of a .env file was requested, make one
    if args.create_dotenv:
        gen_dotenv()

    # Setup is done
    print("Setup is done! Now start the Avoor backend.")

def setup_argparse():
    # Create an argument parser
    parser = argparse.ArgumentParser(
        # Add a simple program description
        description='Sets up Avoor.'
    )
    # Add an argument for the .env generator
    parser.add_argument(
        # Short and full command
        '-e', '--create-dotenv',
        # Make it an on/off flag - True if set (python setup.py -e), False otherwise
        action='store_true',
        # Write the result to args.create_dotenv
        dest="create_dotenv",
        # Help message
        help='whether to create a .env file'
    )
    # Return the parser
    return parser

# If this script isn't imported:
if __name__ == "__main__":
    # Set up the command line parser
    parser = setup_argparse()
    # Parse the arguments
    args = parser.parse_args()
    # Pass them to the setup function
    setup(args)
