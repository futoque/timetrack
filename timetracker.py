from textual import events, on
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll, VerticalGroup, Vertical, Container
from textual.reactive import reactive
from textual.widgets import Button, Digits, Footer, Header, DataTable, TextArea, Input, Label
from textual.validation import Number, Validator
import time
import datetime
import sqlite3

try:
    conn = sqlite3.connect('alltimes.db')
    cursor = conn.cursor()
except sqlite3.OperationalError as e:
    print(f"Database Connection Error: {e}")


class TimeTracker(App):
    CSS_PATH = 'timetracker.tcss'

    gametotal = 0
    lookingtotal = 0
    readingtotal = 0
    cissptotal = 0
    watchingtotal = 0
    programmingtotal = 0

    none: Button = Button("None", id="do_nothing")
    game: Button = Button("Game", id="do_game")
    looking: Button = Button("Looking", id="do_looking")
    reading: Button = Button("Reading", id="do_reading")
    cissp: Button = Button("CISSP", id="do_cissp")
    watching: Button = Button("Watching", id="do_watching")
    programming: Button = Button("Programming", id="do_programming")
    endprogram: Button = Button("Quit", id="do_end")
    log_area: TextArea = TextArea()
    total_area: TextArea = TextArea()

    categories = [none, game, looking, reading, cissp, watching, programming]
    currstart = 0
    currentcategory = 0

    #BINDINGS = [
    #    ("ctrl+q", "save_active_timer", "Save active timer before exit.", show=False, priority=True)
    #]

    def save_to_db(self, category, save_date, diff):
        update_query = f"INSERT INTO timelog (time_type, date, elapsed) VALUES (\"{category}\", \"{save_date}\", {diff})"
        #self.log_area.text += update_query
        try:
            conn = sqlite3.connect('./alltimes.db')
            cursor = conn.cursor()
        except sqlite3.OperationalError as e:
            self.log_area.text += (f"Database Connection Error: {e}")
        try:
            self.log_area.text += update_query
            cursor.execute(update_query)
            conn.commit()
        except sqlite3.Error as e:
            self.log_area.text += (f"Update error: {e}")
        conn.close()

    def add_times(self, diff):
        today = datetime.datetime.now()
        dayout = today.strftime('%Y%m%d')
        match self.currentcategory:
            case 1:
                self.gametotal += diff
                self.log_area.text += "Adding " + str(diff) +" to Game for a total of " + str(self.gametotal) + "\n"
                self.save_to_db("Game", dayout, diff)
            case 2:
                self.lookingtotal += diff
                self.log_area.text += "Adding " + str(diff) + " to Looking for a total of " + str(self.lookingtotal) + "\n"
                self.save_to_db("Looking", dayout, diff)
            case 3:
                self.readingtotal += diff
                self.log_area.text += "Adding " + str(diff) + " to Reading for a total of " + str(self.readingtotal) + "\n"
                self.save_to_db("Reading", dayout, diff)
            case 4:
                self.cissptotal += diff
                self.log_area.text += "Adding " + str(diff) + " to CISSP for a total of " + str(self.cissptotal) + "\n"
                self.save_to_db("CISSP", dayout, diff)
            case 5:
                self.watchingtotal += diff
                self.log_area.text += "Adding " + str(diff) + " to Watching for a total of " + str(self.watchingtotal) + "\n"
                self.save_to_db("Watching", dayout, diff)
            case 6:
                self.programmingtotal += diff
                self.log_area.text += "Adding " + str(diff) + " to Programming for a total of " + str(self.programmingtotal) + "\n"
                self.save_to_db("Programming", dayout, diff)

        updatestring = "Game " + str(datetime.timedelta(seconds=self.gametotal)) + "\nLooking " + str(datetime.timedelta(seconds=self.lookingtotal)) + "\nReading " + str(datetime.timedelta(seconds=self.readingtotal)) + "\nCISSP " + str(datetime.timedelta(seconds=self.cissptotal)) + "\nWatching " + str(datetime.timedelta(seconds=self.watchingtotal)) + "\nProgramming " + str(datetime.timedelta(seconds=self.programmingtotal))
        self.total_area.text = updatestring

    def calc_time(self, category_id):
        timediff = 0
        #self.log_area.text += "clicked " + str(category_id) + " current category " + str(self.currentcategory) + "\n"
        if self.currentcategory != category_id:
            if self.currstart != 0:
                currend = time.time()
                timediff = currend - self.currstart
                self.add_times(timediff)
                self.currentcategory = category_id
                if category_id != 0:
                    self.currstart = currend
                else:
                    self.currstart = 0
            else:
                self.currstart = time.time()
                self.currentcategory = category_id
            return timediff
        else:
            return 0

    def save_active_timer(self):
        self.calc_time(0)
        self.log_area.text += "Saving before exit"
        #time.sleep(6)
        exit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        self.log_area.text += button_id + '\n'

        match button_id:
            case 'do_nothing':
                self.calc_time(0)
            case 'do_game':
                self.calc_time(1)
            case 'do_looking':
                self.calc_time(2)
            case 'do_reading':
                self.calc_time(3)
            case 'do_cissp':
                self.calc_time(4)
            case 'do_watching':
                self.calc_time(5)
            case 'do_programming':
                self.calc_time(6)
            case 'do_end':
                self.save_active_timer()

    def compose(self) -> ComposeResult:
        yield Container(
            self.none,
            self.game,
            self.looking,
            self.reading,
            self.cissp,
            self.watching,
            self.programming,
            self.endprogram,
            id = 'selected',
            classes = 'box'
        )
        yield Container(
            self.log_area,
            id = 'log_area',
            classes = 'box'
        )
        yield Container(
            self.total_area,
            id = 'total_area',
            classes = 'box'
        )


    def on_mount(self) -> None:
        today = datetime.datetime.now()
        dayout = today.strftime('%Y%m%d')
        times_query = f"SELECT time_type, date, SUM(elapsed) FROM timelog WHERE date = {dayout} GROUP BY time_type"
        #times_query = f"SELECT time_type, date FROM timelog WHERE date = {dayout}"
        timeholder = [0, 0, 0, 0, 0, 0]
        try:
            conn = sqlite3.connect('./alltimes.db')
            cursor = conn.cursor()
        except sqlite3.OperationalError as e:
            self.log_area.text += (f"Database Connection Error: {e}")
        try:
            #self.log_area.text += update_query
            cursor.execute(times_query)
            results = cursor.fetchall()
            #self.log_area.text += str(len(results))
            for r in results:
                #self.log_area.text += r
                #self.log_area.text += r[0] + ' ' + str(r[2]) + '\n'
                match r[0]:
                    case "Game":
                        self.gametotal = r[2]
                    case "Looking":
                        self.lookingtotal = r[2]
                    case "Reading":
                        self.readingtotal = r[2]
                    case "CISSP":
                        self.cissptotal = r[2]
                    case "Watching":
                        self.watchingtotal = r[2]
                    case "Programming":
                        self.programmingtotal = r[2]
                updatestring = "Game " + str(datetime.timedelta(seconds=self.gametotal)) + "\nLooking " + str(datetime.timedelta(seconds=self.lookingtotal)) + "\nReading " + str(datetime.timedelta(seconds=self.readingtotal)) + "\nCISSP " + str(datetime.timedelta(seconds=self.cissptotal)) + "\nWatching " + str(datetime.timedelta(seconds=self.watchingtotal)) + "\nProgramming " + str(datetime.timedelta(seconds=self.programmingtotal))
                self.total_area.text = updatestring
        except sqlite3.Error as e:
            self.log_area.text += (f"Query error: {e}")
        conn.close()

app = TimeTracker()
app.run()