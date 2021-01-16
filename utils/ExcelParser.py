import pandas as pd

from utils.Singleton import Singleton
from creators.PollCreator import PollCreator
from creators.StudentCreator import StudentCreator
from creators.SubmissionCreator import SubmissionCreator

class ExcelParser(metaclass=Singleton):

    def __init__(self, poll):
        self.poll = poll

    def _read_max_file_column_count(self, filename: str, delimiter=','):
        # The max column count a line in the file could have
        largest_column_count = 0

        # Loop the data lines
        with open(filename, 'r', encoding='utf-8') as temp_f:
            # Read the lines
            lines = temp_f.readlines()

            for line in lines:
                # Count the column count for the current line
                column_count = len(line.split(delimiter)) + 1

                # Set the new most column count
                largest_column_count = column_count if largest_column_count < column_count else largest_column_count
        return largest_column_count

    def read_students(self, filename: str):
        # next line is for debugging
        # pd.set_option('display.max_rows', None, 'display.max_columns', None, 'display.width', None)
        df: pd.DataFrame = pd.read_excel(filename, header=None)
        df.drop([0, 1, 3, 5, 6, 8, 9], axis=1, inplace=True)
        df = df[pd.to_numeric(df[2], errors='coerce').notnull()]
        df.reset_index(drop=True, inplace=True)
        df.columns = ['studentid', 'firstname', 'lastname', 'repeat']
        sc = StudentCreator()
        for index, row in df.iterrows():
            sc.create_student(
                number=row['studentid'], name=row['firstname'], surname=row['lastname'],
                description=pd.isna(row['repeat'])
            )

    def read_key(self, filename: str = None):
        if filename is None:
            filename = input("Please enter a filename for an answer key file:\n")

        # next line is for debugging
        # pd.set_option('display.max_rows', None, 'display.max_columns', None, 'display.width', None)
        df: pd.DataFrame = pd.read_csv(filename, sep=';', header=None)
        pollname = df[0][0]
        df.drop(inplace=True, axis=0, labels=0)
        df.reset_index(inplace=True, drop=True)
        pc = PollCreator()
        pc.create_poll(pollname)
        # TODO Poll creation logic is flawed, how do we add questions to polls?

    def read_submissions(self, filename: str = None):
        if filename is None:
            filename = input("Please enter a filename for an answer key file:\n")

        # next line is for debugging
        # pd.set_option('display.max_rows', None, 'display.max_columns', None, 'display.width', None)
        df: pd.DataFrame = pd.read_csv(filename, sep=',', index_col=False, header=None, names=range(
            self._read_max_file_column_count(filename)))
        df.dropna(axis=1, how='all', inplace=True)
        df.drop(labels=0, axis=1, inplace=True)
        df.drop(labels=0, axis=0, inplace=True)
        df.reset_index(drop=True, inplace=True)
        sc = SubmissionCreator()
        for index, row in df.iterrows():
            q_and_a = dict()
            for colindex, cell in row.iteritems():
                if colindex < 4 or colindex % 2 == 1:
                    continue
                q_and_a[cell] = row[colindex + 1]
            sc.create_submission(row[1], row[2], row[3], q_and_a)

    def write_poll_outcomes(self, students, submissions):
        for student in students:
            q_a_list = []  # each poll has specific amount of questions, this list holds 1 or 0 depending on answers.
            num_of_questions = None  # each field will reset for each student
            num_of_correct_ans = None
            success_rate = None
            success_percentage = None

            for submission in submissions and submission.poll == self.poll:  # find current poll submissions
                if submission.student == student:  # find student in submission list.

                    for answer in submission.student_answers:  # for each answer in this submission check if it is true.
                        num_of_questions = len(submission.student_answers)

                        if answer.question.trueAnswer == answer:
                            q_a_list.append(1)  # answer matches with true answer
                            num_of_correct_ans += 1
                        else:
                            q_a_list.append(0)  # false

            # calculating rate and percentage
            success_rate = num_of_correct_ans / num_of_questions
            success_percentage = success_rate / 100

            # TODO: This will be printed on excel with pandas.
            print(student.number, student.name, student.surname, student.description, question_list,
                  success_rate, success_percentage, end='\n')

    def write_poll_statistics(self,poll):
        if poll == self.poll:
            for question in poll.poll_questions:
                print(question.description)#bura bak
                for answers in question.all_answers:
                  # TODO: This will be printed on excel with pandas.
                    print(answers +"--->"+ answers.number_of_answer_selection)
                    #There should be a selection counter for Question to determine how many times answer is chosen.
                    #For instance,  first choice is selected by 25 students, second one is 3, third 76, fourth 12 ...

    def write_all_poll_outcomes(self,polls):
        #poll adları dönen for loop
            #write_poll_outcomes(students, submissions):
