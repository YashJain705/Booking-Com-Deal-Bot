from booking.booking import Booking
import time

try:
    with Booking() as bot:
        bot.land_first_page()
        bot.select_currency(currency='INR')
        bot.select_place_to_go(input("Where you want to go ?"))
        time.sleep(2) #time for the calendar to load in        
        bot.select_dates(check_in_date=input("What is the check in date ?"),
                         check_out_date=input("What is the check out date ?"))
        # bot.select_travellers(int(input("How many people ?")))
        bot.select_search()
        bot.apply_filtrations()
        bot.refresh() # A workaround to let our bot to grab the data properly
        bot.report_results()
        input("Wait")

except Exception as e:
    if 'in PATH' in str(e):
        print(
            'You are trying to run the bot from command line \n'
            'Please add to PATH your Selenium Drivers \n'
            'Windows: \n'
            '    set PATH=%PATH%;C:path-to-your-folder \n \n'
            'Linux: \n'
            '    PATH=$PATH:/path/toyour/folder/ \n'
        )
    else:
        raise