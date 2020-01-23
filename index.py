import time
from datetime import datetime
from tkinter import *
import threading


# import notify2  # not working in windows
from win10toast import ToastNotifier


# Start of class
class BreakReminder:

    def __init__(self, main_window):
        self.bg_timer_thread = None
        self.break_at_times = [];
        self.resume_at_times = [];
        print("BreakReminder Obj Has Been Created.")

        # main_frame = Frame(root)  Think about adding this here.

        # Menubar
        self.menu = Menu(main_window)
        main_window.config(menu=self.menu)
        self.file_menu = Menu(self.menu)
        self.file_menu.add_command(label="New Profile", command=self.create_new_profile)
        self.file_menu.add_separator();
        self.file_menu.add_command(label="Exit", command=main_window.quit)
        self.menu.add_cascade(label="File", menu=self.file_menu)

        # Toolbar
        # toolbar = Frame(main_window, bd=1, relief=RAISED)
        # start_button = Button(toolbar, relief=FLAT)
        # start_button.grid(row = 0, column = 0)
        # toolbar.grid(row = 0, column = 0)

        self.label_interval = Label(main_window, text="Interval");
        self.label_duration = Label(main_window, text="Duration");
        self.label_info = Label(main_window, text="All times are measured in minutes");

        self.entry_interval = Entry(main_window);
        self.entry_duration = Entry(main_window);

        self.button_start = Button(main_window, text="Start");
        self.button_quit = Button(main_window, text="Quit");
        self.button_reset = Button(main_window, text="Reset");

    def create_window(self, main_window):

        self.label_interval.grid(row=0, column=0);
        self.label_duration.grid(row=1, column=0);
        self.label_info.grid(row=2, columnspan=2);

        self.entry_interval.grid(row=0, column=1);
        self.entry_duration.grid(row=1, column=1);

        self.button_reset.grid(row=4, column=0)
        self.button_start.grid(row=4, column=1)
        self.button_start.bind("<Button-1>", self.calculate_break_timings)
        self.button_reset.bind("<Button-1>", self.reset_break_timings)

    def create_new_profile(self):
        print("Create new profile clicked")

    def reset_break_timings(self):
        self.button_reset.config(state=DISABLED)
        self.button_start['state'] = NORMAL

        # Kill the thread who is running this process in background.
        if self.bg_timer_thread.is_alive() == TRUE :
            self.bg_timer_thread.stop();
            self.bg_timer_thread.join();


    def calculate_break_timings(self, event):
        """
        This function will start the timing.
        :return:
        """
        print("Inside Break Reminder")

        interval = int(self.entry_interval.get())
        duration = int(self.entry_duration.get())

        if interval <= 0 or duration <= 0:
            print("Interval or Duration is pretty short. Please enter value more than 5.");
            return;

        now = datetime.now().time()  # time object
        print("now =", now)
        print("type(now) =", type(now))

        now_hour = now.hour;
        now_min = now.minute;
        interval_hour = interval // 60  ## Actual hours
        interval_min = interval % 60  ## whatever remaing minutes
        duration_hour = duration // 60
        duration_min = duration % 60

        for i in range(5):

            expected_hour = now_hour + interval_hour
            expected_min = now_min + interval_min

            if expected_min >= 60:
                expected_min = expected_min % 60
                expected_hour = expected_hour + 1
            if expected_hour >= 24:
                expected_hour = expected_hour % 24

            self.break_at_times.append([expected_hour, expected_min])
            now_hour = expected_hour + duration_hour;
            now_min = expected_min + duration_min

            if now_min >= 60:
                now_min = now_min % 60
                now_hour = now_hour + 1
            if now_hour >= 24:
                now_hour = now_hour % 24
            self.resume_at_times.append([now_hour, now_min])

        # End of for loop

        print(self.break_at_times)
        print(self.resume_at_times)
        self.button_start.config(state=DISABLED)
        self.button_reset.config(state=NORMAL)

        self.bg_timer_thread = threading.Thread(target=self.start_break_reminder(), name="bg_timer_thread")

    '''
    def notify(self, title, content):
        #icon_path = ""

        # initialise the d-bus connection
        notify2.init("Break Reminder")

        # create Notification object
        n = notify2.Notification("Break Reminder")

        # Set the urgency level
        n.set_urgency(notify2.URGENCY_NORMAL)

        # Update the content
        n.update(title, content)

        # Show the notification
        n.show()

        # Set the timeout
        n.set_timeout(1000)
    '''

    def notify(self, title, content):
        print("inside notify")

        toaster = ToastNotifier()
        toaster.show_toast(title, content, duration=10)

    def start_break_reminder(self):
        # infinite loop
        while 1 == 1:
            print(self.break_at_times);
            print(self.resume_at_times);
            now = datetime.now().time()  # time object
            #try:
            for i in range(len(self.break_at_times)):
                print("i is for break_at times" +str(i))
                break_at = self.break_at_times[i]
                if break_at[0] == now.hour and break_at[1] == now.minute:
                    print("Showing notification for " + str(self.break_at_times[0]))
                    self.notify("Break time !", "See you in " + str(self.entry_duration.get()) + " minutes")
                    self.break_at_times.pop(0)
                    break
            '''except IndexError:
                print("Index Error occured");
            except :
                print("Exception occred while iterating over break_at_times");
            '''

            #try:
            for r in range(len(self.resume_at_times)):
                print("r is for resume at times" +str(r))
                resume_at = self.resume_at_times[r]
                if resume_at[0] == now.hour and resume_at[1] == now.minute:
                    next_break_at = self.break_at_times[0];
                    print("Showing notification for " + str(self.resume_at_times[0]))
                    self.notify("Its Over !",
                                "I will remind you at " + str(next_break_at[0]) + ":" + str(next_break_at[1]))
                    self.resume_at_times.pop(0)
                    break
            '''except IndexError:
                print("Index Error occured");
            except:
                print("Exception occred while iterating over resume at times");
            '''

            # If we run out of break times
            print("len(self.break_at_times) : "+str(len(self.break_at_times)))
            if len(self.break_at_times) == 0 and len(self.resume_at_times) == 0:
                self.calculate_break_timings("");       #Passing "" is working but need to fix that.

            print("Sleeping for 10 secs")
            time.sleep(10)
            print("10 secs ends")


# end of class BreakReminder

root = Tk()
root.title("Break Reminder")
root.geometry("350x200") #You want the size of the app to be 500x500
root.resizable(0, 0) #Don't allow resizing in the x or y direction
br = BreakReminder(root);
br.create_window(root);
root.mainloop();
