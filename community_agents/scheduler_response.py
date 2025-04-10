import sys
#from Bot1 import bot_response
#from Shell_Agent2 import Shell_Agent
#from Bot_Shell_Agent3 import BotShell_Agent
#from Bot_Shell_MosDEF_Agent4 import BotShell_Agent
import scheduler


# Function to generate a response to user input
def generate_response(user_input):
    # Your logic for generating a response goes here
    #model_response = "test response"
    #model_response = bot_response(user_input)
    #model_response = Shell_Agent(user_input)
    #model_response = BotShell_Agent(user_input)
    model_response = scheduler.Final_Agent(user_input)
    return model_response

if __name__ == "__main__":
    # Get user input from command line
    user_input = sys.argv[1]
    # Generate response
    response = generate_response(user_input)
    
    # Print the response
    print(response)


