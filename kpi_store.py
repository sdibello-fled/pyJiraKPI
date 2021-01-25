import datetime as dt
import calendar

class kpi_store:
    start_date_string = ""
    end_date_string = ""
    now = None
    month = ""
    year = ""
    rapid_view = ""
    project = ""
    sprints = []
    escape_velocity_count = 0
    escape_velocity_percent = 0.0

    sum_completed_issue_count = 0
    sum_completed_issue_initial_estimate_sum = 0
    sum_completed_issue_estimate_sum = 0
    sum_not_completed_issue_count = 0
    sum_not_completed_initial_estimate_sum = 0
    sum_not_completed_estimate_sum = 0
    sum_punted_issue_count = 0
    sum_punted_issue_initial_estimate_sum = 0
    sum_punted_issue_estimate_sum = 0
    sum_issues_completed_in_another_sprint_count = 0
    sum_issues_completed_in_another_sprint_initial_estimate_sum = 0
    sum_issues_completed_in_another_sprint_estimate_sum = 0
    sum_all_issue_estimate_sum = 0
    sum_issues_added_count = 0
    monthly_bug_count = 0
    velocity = 0
    number_of_sprints = 0
    first_time_right = 0
    tech_debt_sum = 0
    stories_less_then_thirteen = 0
    stories_more_then_thirteen = 0
    ability_to_estimate = 0
    gherkin_format_count = 0
    gherkin_kpi = 0
    sprint_churn = 0
    sp_total_on_backlog = 0
    sprint_readiness = 0
    backlog_count_highest = 0
    backlog_count_high = 0
    backlog_count_medium = 0
    backlog_count_low = 0
    created_support_highest = 0
    created_support_high = 0
    created_support_medium = 0
    created_support_low = 0
    completed_support_highest = 0
    completed_support_high = 0
    completed_support_medium = 0
    completed_support_low = 0
    completion_rate = 0

    def update_sums (self):
        self.sum_completed_issue_count = 0
        self.sum_completed_issue_initial_estimate_sum = 0
        self.sum_completed_issue_estimate_sum = 0
        self.sum_not_completed_issue_count = 0
        self.sum_not_completed_initial_estimate_sum = 0
        self.sum_not_completed_estimate_sum = 0
        self.sum_punted_issue_count = 0
        self.sum_punted_issue_initial_estimate_sum = 0
        self.sum_punted_issue_estimate_sum = 0
        self.sum_issues_completed_in_another_sprint_count = 0
        self.sum_issues_completed_in_another_sprint_initial_estimate_sum = 0
        self.sum_issues_completed_in_another_sprint_estimate_sum = 0
        self.sum_all_issue_estimate_sum = 0
        self.sum_issues_added_count = 0
        for sprint in self.sprints:
            self.sum_completed_issue_count += sprint.completed_issue_count
            self.sum_completed_issue_initial_estimate_sum += sprint.completed_issue_initial_estimate_sum
            self.sum_completed_issue_estimate_sum += sprint.completed_issue_estimate_sum
            self.sum_not_completed_issue_count += sprint.not_completed_issue_count
            self.sum_not_completed_initial_estimate_sum += sprint.not_completed_initial_estimate_sum
            self.sum_not_completed_estimate_sum += sprint.not_completed_estimate_sum
            self.sum_punted_issue_count += sprint.punted_issue_count
            self.sum_punted_issue_initial_estimate_sum += sprint.punted_issue_initial_estimate_sum
            self.sum_punted_issue_estimate_sum += sprint.punted_issue_estimate_sum
            self.sum_issues_completed_in_another_sprint_count += sprint.issues_completed_in_another_sprint_count
            self.sum_issues_completed_in_another_sprint_initial_estimate_sum += sprint.issues_completed_in_another_sprint_initial_estimate_sum
            self.sum_issues_completed_in_another_sprint_estimate_sum += sprint.issues_completed_in_another_sprint_estimate_sum
            self.sum_all_issue_estimate_sum += sprint.all_issue_estimate_sum 
            self.sum_issues_added_count += sprint.issues_added_count

    def calculate_velocity (self):
        #there are two teams, how many actual sprints are there
        self.number_of_sprints = 0
        self.number_of_sprints = len(self.sprints)
        self.velocity = self.sum_completed_issue_estimate_sum / (self.number_of_sprints / 2)


    def calculate_escape_velocity (self):
        self.update_sums()
        if (self.sum_completed_issue_count > 0):
            self.escape_velocity_percent = self.escape_velocity_count / self.sum_completed_issue_count

    def setdates (self):
        current_year = self.year
        last_day_of_month = calendar.monthrange(current_year, self.month)[1]
        self.start_date_string = f'{current_year}-{self.month}-01'
        self.end_date_string = f'{current_year}-{self.month}-{last_day_of_month}'
    
    def calculate_first_time_right(self):
        numerator = self.sum_completed_issue_initial_estimate_sum + self.sum_punted_issue_initial_estimate_sum + self.sum_issues_completed_in_another_sprint_initial_estimate_sum
        denomerator = self.sum_completed_issue_estimate_sum + self.sum_punted_issue_estimate_sum + self.sum_issues_completed_in_another_sprint_estimate_sum
        self.first_time_right = 100
        if denomerator > 0:
            self.first_time_right = numerator / denomerator

    def calcuate_ability_to_estimate(self):
        self.ability_to_estimate = 100 - (self.stories_more_then_thirteen / self.stories_less_then_thirteen)

    def calcuate_gherkin_kpi(self):
        self.gherkin_kpi = (self.gherkin_format_count / self.sum_completed_issue_count)

    def calculate_sprint_churn(self):
        self.sprint_churn = 0
        if self.sum_completed_issue_estimate_sum + self.sum_punted_issue_estimate_sum + self.sum_not_completed_estimate_sum > 0:
            self.sprint_churn = self.sum_punted_issue_estimate_sum / (self.sum_completed_issue_estimate_sum + self.sum_punted_issue_estimate_sum + self.sum_not_completed_estimate_sum)

    def calculate_sprint_readiness(self):
        if self.velocity > 0:
            self.sprint_readiness = self.sp_total_on_backlog / self.velocity

    ## Story points attempted by story points completed
    def calculate_completion_rate(self):
        self.completion_rate = (self.sum_completed_issue_estimate_sum/self.sum_completed_issue_initial_estimate_sum)
        if self.completion_rate > 1:
            self.completion_rate = 1

    def __init__(self ):
        self.now = dt.datetime.now()
        self.sprints = []
        self.escape_velocity_count = 0

