import os
import sys
from datetime import date
from lib.history_class import History

program_name, *args = sys.argv

today = date.today()
start_date = args[0]
end_date = args[1] if len(args) >= 2 else today

# start_date = '2021-04-03'
# end_date = '2021-04-04'

folder = f'start-{start_date}_end-{end_date}_on-{today}/'
print(folder)

dir_ = os.path.dirname(os.path.abspath(__file__)) + "/data/history/" + folder

if __name__ == "__main__":

    history = History(dir_, start_date, end_date)
    history.scrape()
    history.parse()
