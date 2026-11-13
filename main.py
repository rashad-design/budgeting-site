from bakery import assert_equal
from dataclasses import dataclass
from drafter import *
import uuid


add_website_css("""
.dark-mode {
    background-color: #121212;
    color: white;
    min-height: 100vh;
    width: 100%;
    padding: 20px;
    box-sizing: border-box;
}

.dark-mode h1,
.dark-mode h2,
.dark-mode h3,
.dark-mode p,
.dark-mode label {
    color: white;
}

.light-mode {
    background-color: white;
    color: black;
    min-height: 100vh;
    width: 100%;
    padding: 20px;
    box-sizing: border-box;
}
""")

set_site_information(
    author= "Rashad Cherkaoui",
    description= "Bill Buddy",
    sources= "I used the drafter docs for the most part and also used chatgpt to help me with just the css/div design alignment. The LLM conversation is in the links section.",
    planning= "",
    links= ["https://github.com/rashad-design/budgeting-site", "https://chatgpt.com/share/6af5f3bb-4a48-83ea-b87e-36ccbef00dea"]
    )


@dataclass
class Bill:
    unique_id: str
    name: str
    price: float
    paid: bool
    '''
    This is a Bill class used to create info for each bill
    
    Fields:
    unique_id(str): The unique uuid for the bill
    name(str): The name of the bill created
    price(float): The price of the bill created
    paid(bool): The status of the bill if it has been paid or not
    '''


@dataclass
class Settings:
    dark_mode: bool
    '''
    This is a Settings class used to create/saving info for the settings page
    
    Fields:
    dark_mode(bool): Changes between light and dark mode
    '''


@dataclass
class State:
    bills: list[Bill]
    message: str
    budget: float
    quiz_taken: bool
    settings: Settings
    
    '''
    This is a State class used to save/mutate info
    
    Fields:
    bills(list[Bill]): The list that stores all bills
    message(str): The status message of the current page
    budget(float): The budget value you input to calculate math
    quiz_taken(bool): Flags if the financial quiz has been taken
    settings(Settings): Settings that will be saved
    '''


#Financial Quiz section----------------------------------------------------------------------------------------------
@route
def index(state: State)-> Page:
    '''
    This function displays creates the finance quiz questions/inputs
    
    Args:
    state(State): The state for the page
    
    Return:
    Returns a new page which displays the finance quiz
    '''
    
    if not state.quiz_taken:
        return Page(state, [
            change_text_align(Header("Financial Quiz"), "center"),
            "\n",
            "Are you in debt? (If you answer no please skip the the rest of the questions.)",
            SelectBox("is_in_debt", ["No", "Yes"]),
            "\n",
            "If you are in any debt, how much debt are you in?",
            TextBox("debt_amt", 0.0, "number"),
            "\n",
            "How much do you make per year?",
            TextBox("salary", 0.0, "number"),
            "\n",
            "What debt percentage would you like to select for an estimated pay per month for your debt?",
            TextBox("debt_percentage", 0, "number"),
            "\n",
            Button("Complete", "quiz_completed")
        ])


@route
def quiz_completed(state: State, is_in_debt: bool, debt_amt: float, salary: float, debt_percentage: int)-> Page:
    '''
    This function displays feedback after you have finished the quiz and calculates
    how much you should pay per month for your debt(if you have one).
    
    Args:
    state(State): The state for the page
    
    Return:
    Returns a new page which displays the feedback after you've completed the finance quiz
    '''


    state.quiz_taken = True
    if not is_in_debt:
        return Page(state, [
            change_text_align(Header("Financial Quiz"), "center"),
            change_text_align(Text("Since you do not have a debt, I hope you can use this website for budgeting or any other reasons!"), "center"),
            "\n",
            Button("Next", "home_page")
        ])
        
    else:
        salary_per_month = salary // 12
        percent_to_decimal = debt_percentage // 100
        to_pay_per_month = salary_per_month * percent_to_decimal
        return Page(state, [
            change_text_align(Header("Financial Quiz"), "center"),
            change_text_align(Text("Since you have a debt of $" + str(debt_amt) +", based on your salary of $" + str(salary) +", I recommend you pay $" + str(to_pay_per_month) +" per month toward your debts"), "center"),
            "\n",
            Button("Next", "home_page")
        ])


#Themes for pages
def create_page(state: State, content: list) -> Page:
    if state.settings.dark_mode:
        theme = "dark-mode"
    else:
        theme = "light-mode"

    return Page(state, [
        Div(
            *content,
            classes=theme
        )
    ])


#Homepage section--------------------------------------------------------------------------------------------
@route
def home_page(state: State)-> Page:
    '''
    This function takes you to the homepage where you can view your bills and delete them
    
    Args:
    state(State): The state for the page
    
    Return:
    Returns a new page which displays your bills' info with a delete button
    '''


    if not state.bills:
        state.message = "No bills created yet"
    else:
        state.message = "Here is your homepage"

    bill_elements = []

    for bill in state.bills:
        bill_elements.append(create_box(bill))

    return create_page(state, [
        change_text_align(Header("Budget Buddy: Home"), "center"),
        change_text_align(Text("Welcome to Budget Buddy!"), "center"),
        change_text_align(Text(state.message), "center"),

        "\n",

        Button("Home", "home_page"),
        Button("Bills", "bills_page"),
        Button("Budgeting", "budget_page"),
        Button("Settings", "settings_page"),

        Div(
            *bill_elements,
            style={
                "display": "flex",
                "flexDirection": "row",
                "flexWrap": "wrap",
                "alignItems": "center",
                "justifyContent": "center",
                "gap": "15px",
                "width": "100%"
            }
        )
        
    ])


@route
def create_box(bill: Bill)-> PageContent:
    '''
    This function creates the visual template where the info is displayed to the user
    
    Args:
    bill(Bill): The bill that should be created visually
    
    Return:
    Returns a page content which has info about the the bill/creates a box with info
    '''
    
    option = "No"
    
    if bill.paid:
        option = "Yes"
        
    return Div(
        Header("Name: " + str(bill.name)),
        Header("Price: $" + str(bill.price)),
        Header("Paid: " + option),
        Button("Delete " + str(bill.name), "delete_bill", arguments=[("unique_id", bill.unique_id)])
        )

#Billspage section--------------------------------------------------------------------------------------------------
@route
def bills_page(state: State)-> Page:
    '''
    This function creates the bills page where the user can put in their inputs and add the bill
    
    Args:
    state(State): The state for the page
    
    Return:
    Returns a new page which displays the areas where you can create your bill
    '''
    
    state.message = "Please input a name, price, and status of your bill."

    return create_page(state, [
            change_text_align(Header("Bills"), "center"),
            "\n", state.message,
            "\n",
            "Bill Name:", TextBox("name", "", "text"),
            "\n",
            "Bill Price:", TextBox("price", 0.0, "number"),
            "\n",
            "Paid?:", SelectBox("paid", ["Yes", "No"]),
            "\n",
            Button("Cancel", "home_page"),
            Button("Add", "create_bill")
        ])


@route
def create_bill(state: State, name: str, price: float, paid: bool)-> Page:
    '''
    This function creates a bill with a unique id based on the inputs from the user
    
    Args:
    state(State): The state for the page
    name(str): Name of the bill
    price(float): Price of the bill
    paid(bool): If the bill has been paid
    
    Return:
    Returns the homepage route with the state
    '''
    
    unique = str(uuid.uuid4())
    new_bill = Bill(unique, str(name), float(price), bool(paid))
    state.bills.append(new_bill)
    return home_page(state)
   

@route
def delete_bill(state: State, unique_id: str)-> Page:
    '''
    This function deletes the bill from the bill's list based on it's unique id
    
    Args:
    state(State): The state for the page
    unique_id(str): A special unique id that is generated via a uuid
    
    Return:
    Returns the homepage route with the state
    '''
    
    print(unique_id)
    for bill in state.bills:
        if bill.unique_id == unique_id:
            state.bills.remove(bill)
            break
    return home_page(state)


#Budgetpage section---------------------------------------------------------------------------------------------------
def get_paid_bills(state: State)-> list[Bill]:
    paid_bills = []
    
    for bill in state.bills:
        if bill.paid:
            paid_bills.append(bill)
            
    return paid_bills


@route
def budget_page(state: State)-> Page:
    state.message = "Please enter your budget for the month. This will calculate how much is left over by deducting the paid bills only."
    return create_page(state, [
        change_text_align(Header("Settings Menu"), "center"),
        change_text_align(Text(state.message), "center"),
        "\n",
        "Budget: ", TextBox("budget", 0.0, "number"),
        "\n",
        Button("Cancel", "home_page"),
        Button("Calculate", "calculate_budget")
    ])


@route
def calculate_budget(state: State, budget: float)-> Page:
    state.budget = budget
    paid_bills = get_paid_bills(state)
    total = 0
    
    for bill in paid_bills:
        total += bill.price
    
    leftover_amt = state.budget - total
    
    text_msg = "Please enter your budget for the month. This will calculate how much of your budget is left by deducting the paid bills."
    state.message = "Your leftover budget is: " + str(leftover_amt)
    
    return create_page(state, [
        change_text_align(Header("Settings Menu"), "center"),
        change_text_align(Text(text_msg), "center"),
        "\n",
        "Budget: ", TextBox("budget", 0.0, "number"),
        "\n",
        Button("Cancel", "home_page"),
        Button("Calculate", "calculate_budget"),
        "\n",
        change_text_align(Text(state.message), "center")
    ])


#Settingspage section-------------------------------------------------------------------------------------------------------    
@route
def settings_page(state: State)-> Page:
    state.message = "Edit settings to your preference."
    return create_page(state, [
        change_text_align(Header("Settings Menu"), "center"),
        change_text_align(Text(state.message), "center"),
        "\n",
        "Turn on dark mode", Button("Mode", "toggle_dark_mode"),
        "\n",
        Button("Return to home", "home_page"),
    ])


@route
def toggle_dark_mode(state: State)-> Page:
    state.settings.dark_mode = not state.settings.dark_mode
    return settings_page(state)


start_server(State([], "", 0.0, False, Settings(False)))
