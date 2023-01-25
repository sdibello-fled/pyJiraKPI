class sprint_velocity_store:

    sprintId:0
    sprintName:""
    completed_issue_count = 0
    completed_issue_initial_estimate_sum = 0
    completed_issue_estimate_sum = 0
    not_completed_issue_count = 0
    not_completed_initial_estimate_sum = 0
    not_completed_estimate_sum = 0
    punted_issue_count = 0
    punted_issue_initial_estimate_sum = 0
    punted_issue_estimate_sum = 0
    issues_completed_in_another_sprint_count = 0
    issues_completed_in_another_sprint_initial_estimate_sum = 0
    issues_completed_in_another_sprint_estimate_sum = 0
    all_issue_estimate_sum = 0
    issues_added_count = 0
    issues_added = []
    compelted_issues = []    
    not_completed_issues = []
    punted_issues = []
    complete_in_another_sprint = []
    defects_created = []

    #def __new__(self, id):
    #    sprintId = id

    def __init__(self, id):
        sprintId= 0
        sprintName =""
        completed_issue_count = 0
        completed_issue_initial_estimate_sum = 0
        completed_issue_estimate_sum = 0
        not_completed_issue_count = 0
        not_completed_initial_estimate_sum = 0
        not_completed_estimate_sum = 0
        punted_issue_count = 0
        punted_issue_initial_estimate_sum = 0
        punted_issue_estimate_sum = 0
        issues_completed_in_another_sprint_count = 0
        issues_completed_in_another_sprint_initial_estimate_sum = 0
        issues_completed_in_another_sprint_estimate_sum = 0
        all_issue_estimate_sum = 0
        issues_added_count = 0
        issues_added = []
        compelted_issues = []    
        not_completed_issues = []
        punted_issues = []
        complete_in_another_sprint = []
        defects_created = []