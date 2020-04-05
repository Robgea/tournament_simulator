import csv
import random

class Team():
    def __init__(self, name, school, abbr):
        self.name = name
        self.opp_list = set()
        self.judge_list = set()
        self.school = school
        self.abbr = abbr

    def __repr__(self):
        return f'{self.name}'

class Judge():
    def __init__(self, name, school, round_limit):
        self.name = name
        self.school = school
        self.round_limit = int(round_limit)
        self.done_flag = False
        self.rounds_judged = 0

    def __repr__(self):
        return f'{self.name}'

    def round_check(self):
        if self.rounds_judged == self.round_limit:
            self.done_flag = True
            return True
        else:
            return False

def team_list_maker():
    team_csv = open('team_list.csv')
    team_reader = csv.reader(team_csv)
    team_list = list(team_reader)
    output_list = []
    for team in team_list:
        team_name = f'{team[0]} {team[1]}'
        team_abbr = team[2]
        if team_abbr.startswith('Michigan'):
            if team_abbr.startswith('Michigan St'):
                school = 'Mich State'
            else:
                school = 'U Mich'
        elif team_abbr.startswith('George'):
            school = team[0]
        else:
            if (len(team[2]) < 9):
                school = team[2][0:4]
            else: 
                school = team[2][0:7]
        entry = Team(team_name, school, team_abbr)
        output_list.append(entry)

    return output_list

def room_list_maker():
    room_csv = open('room_list.csv')
    csv_reader = csv.reader(room_csv)
    csv_list = list(csv_reader)
    room_output = [room[0] for room in csv_list]
    return room_output

def judge_list_maker():
    judge_csv = open('judge_list.csv')
    judge_reader = csv.reader(judge_csv)
    raw_judge_list = list(judge_reader)
    judge_output = []

    for row in raw_judge_list:
        judge_name = f'{row[0]} {row[1]}'
        judge_school = row[2]
        round_limit = row[4]
        entry = Judge(judge_name, judge_school, round_limit)
        judge_output.append(entry)

    return judge_output



def random_pairing_generator(entry_list, judge_list, room_list, rounds):
    round_count = 0
    final_output = []
    unpaired_teams = entry_list
    judging_pool = judge_list
    depleted_judges = set()
    
    while round_count < (rounds + 1):
        paired_teams = []
        output_list = []
        round_count += 1
        unassigned_judges = judging_pool
        assigned_judges = []
        pairing_status = False
        round_2 = False
        unassigned_aff = []
        unassigned_neg = []
        unassigned_rooms = room_list
        assigned_rooms = []


        while pairing_status == False:
            try:
                unpaired_teams = list(set(unpaired_teams) - set(paired_teams))
                unassigned_rooms = list(set(unassigned_rooms) - set(assigned_rooms))
                if  len(unpaired_teams) == 0:
                    final_output.append(output_list)
                    unassigned_judges = list(set(unassigned_judges) - set(assigned_judges))
                    pairing_status == True
                    break
                unassigned_judges = list(set(unassigned_judges) - set(assigned_judges))
                pairing = random.sample(unpaired_teams, 2)
                if (school_check(pairing[0], pairing[1]) == True) and (len(unpaired_teams) > 2):
                    print(f'We have team on team violence! {pairing[0]}{pairing[1]}\n')
                    continue
                elif (opp_check(pairing[0], pairing[1]) == True) and (len(unpaired_teams) > 2):
                    print(f'We have a rematch! {pairing[0]} and {pairing[1]} \n With prior pairings: {pairing[0].opp_list} \n {pairing[1].opp_list}')
                    continue
                else:
                    pairing[0].opp_list.add(pairing[1])
                    pairing[1].opp_list.add(pairing[0])
                    unassigned_aff.append(pairing[1])
                    unassigned_neg.append(pairing[0])
                    for team in pairing:
                        paired_teams.append(team)

                    assignable_judges = list(set(unassigned_judges) - (pairing[0].judge_list.union(pairing[1].judge_list)))
                    panel = random.sample(assignable_judges, 3)
                    room = random.choice(unassigned_rooms)
                    assigned_rooms.append(room)
                    output_list.append([room, pairing[0], pairing[1], panel[0], panel[1], panel[2]])
                    for judge in panel:
                        assigned_judges.append(judge)
                        pairing[0].judge_list.add(judge)
                        pairing[1].judge_list.add(judge)
                        judge.rounds_judged += 1
                        if judge.round_check() == True:
                            depleted_judges.add(judge)
                            print(f'Judge: {judge} depleted after {judge.rounds_judged} rounds!\n')

            except Exception as err:
                print(f'Error: {err}\n Paired teams: {paired_teams} \n Unpaired teams: {unpaired_teams}, {len(unpaired_teams)}\n')


        judging_pool = list((set(unassigned_judges).union(assigned_judges)) - depleted_judges) 



        assigned_aff = []
        assigned_neg = []
        second_output = []
        unassigned_judges = judging_pool
        assigned_judges = []
        unassigned_rooms = room_list
        assigned_rooms = []
        while round_2 == False:

            unassigned_aff = list(set(unassigned_aff) - set(assigned_aff))
            unassigned_neg = list(set(unassigned_neg) - set(assigned_neg))
            unassigned_judges = list(set(unassigned_judges) - set(assigned_judges))
            unassigned_rooms = list(set(unassigned_rooms) - set(assigned_rooms))
            if len(unassigned_aff) == 0:
                final_output.append(second_output)
                paired_teams = list(set(assigned_aff).union(assigned_neg))
                round_2 == True
                break
            aff_choice = random.choice(unassigned_aff)
            if len(unassigned_neg) > 1:
                assignable_neg = list(set(unassigned_neg) - set(aff_choice.opp_list))
                neg_choice = random.choice(assignable_neg)
                if (school_check(aff_choice, neg_choice) == True):
                    continue
                else:
                    aff_choice.opp_list.add(neg_choice)
                    neg_choice.opp_list.add(aff_choice)
                    assigned_neg.append(neg_choice)
                    assigned_aff.append(aff_choice)
                    assignable_judges = list(set(unassigned_judges) - (aff_choice.judge_list.union(neg_choice.judge_list)))
                    panel = random.sample(assignable_judges, 3)

                    room = random.choice(unassigned_rooms)
                    assigned_rooms.append(room)
                    second_output.append([room, aff_choice, neg_choice, panel[0], panel[1], panel[2]])
                    for judge in panel:
                        assigned_judges.append(judge)
                        aff_choice.judge_list.add(judge)
                        neg_choice.judge_list.add(judge)
                        judge.rounds_judged += 1
                        if judge.round_check() == True:
                            depleted_judges.add(judge)
                            print(f'Judge: {judge} depleted after {judge.rounds_judged} rounds!\n')


            else:
                neg_choice = unassigned_neg[0]
                aff_choice.opp_list.add(neg_choice)
                neg_choice.opp_list.add(aff_choice)
                assigned_neg.append(neg_choice)
                assigned_aff.append(aff_choice)
                assignable_judges = list(set(unassigned_judges) - (aff_choice.judge_list.union(neg_choice.judge_list)))
                panel = random.sample(assignable_judges, 3)
                room = random.choice(unassigned_rooms)
                second_output.append([room, aff_choice, neg_choice, panel[0], panel[1], panel[2]])
                for judge in panel:
                    assigned_judges.append(judge)
                    aff_choice.judge_list.add(judge)
                    neg_choice.judge_list.add(judge)
                    judge.rounds_judged += 1
                    if judge.round_check() == True:
                        depleted_judges.add(judge)
                        print(f'Judge: {judge} depleted after {judge.rounds_judged} rounds!\n')

        judging_pool = list((set(unassigned_judges).union(assigned_judges)) - depleted_judges) 

        unpaired_teams = paired_teams

    return final_output

def opp_check(a, b):
    if a in b.opp_list:
        return True
    else:
        return False

def school_check(a, b):
    if a.school == b.school:
        return True
    else:
        return False


def pairing_writer(list_of_pairings):

    round_num = 1

    for pairing in list_of_pairings:
        print(f'Round the {round_num}: \n \n')
        round_csv = open(f'round_the_{round_num}.csv', 'w', newline = '', encoding='utf-8')
        csv_write = csv.writer(round_csv)
        csv_write.writerow(['Room','Affirmative', 'Negative', 'Judge 1', 'Judge 2', 'Judge 3']) 

        for pair in pairing:
            csv_write.writerow(pair)
        round_num += 1


def judge_test(judge_list):
    run_count = 1
    while run_count < 9:
        print(f'Round the {run_count}: \n')
        for judge in judge_list:
            judge.round_check()
            if judge.done_flag == False:
                judge.rounds_judged += 1
            else:
                continue

            print(f'Judge: {judge}  Rounds Judged: {judge.rounds_judged} Round Limit:{judge.round_limit} \n')

        run_count += 1




room_list = room_list_maker()
test_list = team_list_maker()
judging_list = judge_list_maker()
test_output = random_pairing_generator(test_list, judging_list, room_list,3)
pairing_writer(test_output)




