import openpyxl
from openpyxl.worksheet.table import Table, TableStyleInfo, TableColumn
from kpi import kpi_month


class excel_kpi:
    Headers = ['Sprint Completeion Rate', 'Escape Velcoity Rate', 'Requirements in Gherkin', 'Sprint Readiness', 'Sprint Churn', 'Tech Debt Paydown']
    currentWorkbook = None 
    ws = None

    # constructor
    def __init__(self, excel_path): 
        self.table_kpi_name = "KPIs"
        self.file_path = ""
        self.currentWorkbook = None
        self.ws = None
        self.tab = None
        self.filename = excel_path
        self.headers = ['SprintCompRate', 'EscVelRate', 'ReqInGherkin', 'SprintReadiness', 'SprintChurn', 'TechDebtPaydown']
        if len(excel_path) <= 0:
            raise print("file path can't be 0")
        try:
            self.currentWorkbook = openpyxl.load_workbook(filename=excel_path)
        except:
            print("couldn't open spreadsheet")
    
    def set_sheet(self, sheet_name):
        try:
            self.ws = self.currentWorkbook.get_sheet_by_name(sheet_name)
        except:
            print(f"set_sheet: {sheet_name} wasn't found, creating")
            self.ws = self.currentWorkbook.create_sheet(sheet_name)
        return True

    def set_table(self, project):
        try:
            table = self.ws.tables[self.table_kpi_name]
        except:
            table = Table(displayName='KPIs')
            for column, value in zip(table.tableColumns, self.headers):
                column.name = value
            self.tab = table
        return True

    def save_file(self):
        try:
            self.currentWorkbook.save(self.filename)
        except:
            print("Fails to save file")
            return False
        return True

    #set the data to the table
    def set_data(self, kpi:kpi_month):
        if len(kpi.team_descriptor) > 0:
            sheet_name = kpi.project+"-"+kpi.team_descriptor
        else:
            sheet_name = kpi.project
        self.set_sheet(sheet_name)

        self.ws.append([kpi.Sprint_Completion_Rate, kpi.Escape_Velocity_Rate, kpi.Gherkin_Story_Rate, kpi.Sprint_Readiness_Ratio, kpi.Sprint_Churn, kpi.Tech_Debt_Paydown_Ratio])
        return


    def add_row(self):
        #adds a row, or moves ot the next row       
        return

    def write_cols(self):
        #push the data to the sheet
        return
    
    def write_sheet(self, project, month, year, kpi_data):
        return