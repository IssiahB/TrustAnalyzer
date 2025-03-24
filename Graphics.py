import tkinter as tk
from tkinter import ttk
import TrustScraper as ts

# TODO When button pressed should switch page to ScrapePage
# TODO When button pressed should handle getting page count from source webpage
# TODO Edit process_request function in TrustScraper Module to allow for getting just page count so user can input desired page scan quantity
# TODO Potentially extract functionallity into seperate funtion for above todo

def construct_categories() -> list:
    return [
            "animals_pets",
            "food_beverages_tobacco",
            "money_insurance",
            "beauty_wellbeing",
            "public_local_services",
            "health_medical",
            "business_services",
            "restaurants_bars",
            "construction_manufacturing",
            "hobbies_crafts",
            "shopping_fashion",
            "home_garden",
            "education_training",
            "sports",
            "electronics_technology",
            "home_services",
            "travel_vacation",
            "events_entertainment",
            "legal_services_government",
            "utilities",
            "media_publishing",
            "vehicles_transportation"
        ]

class TrustPilotApp:
    def __init__(self, root):
        self.scrape_category = construct_categories()

        self.root = root
        self.root.title("TrustPilot Analyser")
        self.root.geometry("700x500")

        # Store all pages in dictionary
        self.pages = {}

        for P in (CategoryPage, ScrapePage):
            frame: ttk.Frame = P(self.root, self)
            self.pages[P] = frame
            frame.pack()

        self.show_page(CategoryPage)
    
    def show_page(self, page: ttk.Frame):
        """ Raises the requested page to the top"""
        frame: ttk.Frame = self.pages[page]
        frame.lift()

    def create_context(self, category):
        self.context = ts.ScrapperContext(self, category)

    def exit_program(self):
        self.root.quit()
        self.root.destroy()

class CategoryPage(ttk.Frame):
    def __init__(self, root: ttk.Frame, controller: TrustPilotApp):
        ttk.Frame.__init__(self, root)
        self.root = root
        self.controller = controller

        title_frame = ttk.Frame(self)
        title_frame.grid(row=0, column=0)
        ##### Title Section
        title_label = ttk.Label(title_frame, text="TrustPilot Analyser", font=("Modern", 24, "bold") )
        title_label.pack(padx=100, pady=50, expand=True)

        cat_frame = ttk.Frame(self)
        cat_frame.grid(row=1, column=0, rowspan=3)
        ##### Category Section
        # Category Label
        cat_label = ttk.Label(cat_frame, text="Select Scrape Category:", font=("Modern", 12))
        cat_label.pack(side="left", padx=20)
        # Category Dropdown
        self.category_value = tk.StringVar(value=controller.scrape_category[0]) # Default Value
        category_dropdown = ttk.Combobox(cat_frame, textvariable=self.category_value, values=controller.scrape_category)
        category_dropdown.pack(side="right", padx=20, pady=20)

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=4, column=0, rowspan=2, pady=20)
        ##### Button Section
        page_btn = ttk.Button(btn_frame, text="Get Page Count", command=self.btn_press)
        page_btn.pack()

        self.columnconfigure(0, weight=1, minsize=600)

    def btn_press(self):
        category = self.category_value.get()
        self.controller.create_context(category)


class ScrapePage(ttk.Frame):
    def __init__(self, root: ttk.Frame, controller: TrustPilotApp):
        ttk.Frame.__init__(self, root)



if __name__ == "__main__":
    root = tk.Tk()
    app = TrustPilotApp(root)
    root.protocol("WM_DELETE_WINDOW", app.exit_program)
    root.mainloop()