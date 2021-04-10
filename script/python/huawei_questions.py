# -*- coding:utf-8 -*-
# !/usr/bin/python3
import json
import random
import re
from sys import argv
import pandas as pd


def get_args():
    if len(argv) < 2:
        print("请设置需要解析的txt文件")
        return
    txt_path = argv[1]

    if len(argv) >= 3:
        output_path = argv[2]
    else:
        output_path = txt_path.replace('.txt', '.xlsx')

    return txt_path, output_path


def json_encoder(o):
    return o.__dict__


class Option:

    def __init__(self, option_num, value):
        value = value.lstrip().rstrip()
        self.optionNum = option_num
        self.value = value
        self.flag = 0

    def append_value(self, new_line):
        new_line = new_line.lstrip().rstrip()
        self.value += new_line


class Question:

    def __init__(self, index):
        self.index = int(index)
        self.question = ''
        self.options = []
        self.answers = ''
        self.multi = False

    def append_question_content(self, new_line):
        self.question += new_line

    def add_option(self, matched_option):
        option_num = matched_option.group(1)
        value = matched_option.group(2)
        self.options.append(Option(option_num, value))

    def set_answer(self, answers):
        if not answers:
            return
        self.answers = answers
        answers = answers.lstrip().rstrip()
        self.multi = len(answers) > 1
        for ch in answers:
            for item in self.options:
                if item.optionNum == ch:
                    item.flag = 1
                    break

    def append_option_content(self, new_line):
        self.options[len(self.options) - 1].append_value(new_line)

    def get_answer_value(self):
        for ch in self.answers:
            for item in self.options:
                if item.optionNum == ch:
                    return item.value

WAIT_QUESTION = 0
'''等待问题开始'''
QUESTION_START = 1
'''问题开始'''
OPTION_START = 2
'''等待问题开始'''

DIFFICULTIES = ['一般', '容易', '困难']


def write_to_excel(all_questions, excel_path):
    rows = []
    for item in all_questions:
        if not item.answers:
            continue
        row = [
            '知识竞赛',
            '多选题' if item.multi else '单选题',
            '文本题',
            random.choice(DIFFICULTIES),
            '华为,H12',
            item.question,
            json.dumps(item.options, default=json_encoder),
            '',
            item.answers,
            '1',
            '1'
        ]
        rows.append(row)
        if not item.multi:
            answer_value = item.get_answer_value()
            if answer_value and len(answer_value) < 12:
                if len(item.options) == 2 and (answer_value == '正确' or answer_value == '错误'):
                    row = [
                        '知识竞赛',
                        '判断题',
                        '文本题',
                        random.choice(DIFFICULTIES),
                        '华为,H12',
                        item.question + '\u000D\u000A',
                        # 选项
                        json.dumps(item.options, default=json_encoder),
                        '',
                        answer_value,
                        '1',
                        '1'
                    ]
                    rows.append(row)
                else:
                    row = [
                        '知识竞赛',
                        '填空题',
                        '文本题',
                        random.choice(DIFFICULTIES),
                        '华为,H12',
                        item.question + '\u000D\u000A',
                        # 选项
                        '',
                        '',
                        answer_value,
                        '2',
                        '2'
                    ]
                    rows.append(row)

    df = pd.DataFrame(rows,
                      columns=['应用类型', '试题类型', '题型', '难易度', '标签', '题干', '选项', '文件地址', '答案', '正确得分', '错误扣分'])
    df.to_excel(excel_path, sheet_name="sheet1", index=False)
    pass


def parse_questions(txt_path, excel_path, expect_len, tags):
    q_start_re = re.compile(r'^QUESTION (\d+)$')
    choose_re = re.compile(r'^([A-Z])\.(.*)$')
    answers_re = re.compile(r'^((Correct Answer)|(CorrectAnswer)):\s*(.*)\s*$')
    all_questions = []
    line_number = 0
    with open(txt_path, 'r', encoding="utf8") as txt_file:
        state = WAIT_QUESTION
        question = None
        for line in txt_file:
            line_number += 1
            if line_number == 312:
                print(line)
            if state == WAIT_QUESTION:
                match_start = q_start_re.match(line)
                if match_start:
                    state = QUESTION_START
                    # 找到题目
                    question = Question(match_start.group(1))
                    all_questions.append(question)
                continue
            elif state >= QUESTION_START:
                line = line.lstrip().rstrip()
                if line:
                    if state == QUESTION_START:
                        # 检查是否是题目的开始
                        matched_option = choose_re.match(line)
                        if matched_option:
                            state = OPTION_START
                            question.add_option(matched_option)
                        else:
                            # 增加题干
                            question.append_question_content(line)

                    elif state == OPTION_START:
                        matched_option = choose_re.match(line)
                        if matched_option:
                            # 新的选项
                            question.add_option(matched_option)
                        else:
                            # 是否是答案
                            matched_answers = answers_re.match(line)
                            if matched_answers:
                                # 答案
                                question.set_answer(matched_answers.group(4))
                                state = WAIT_QUESTION
                                question = None
                            else:
                                # 选项内容
                                question.append_option_content(line)

    length = len(all_questions)
    print(length)
    if expect_len != length:
        not_found = []
        for i in range(1, expect_len + 1):
            find = False
            for item in all_questions:
                if item.index == i:
                    find = True
                    break
            if not find:
                not_found.append(i)
        print("解析失败的题目索引")
        print(not_found)
        return

    write_to_excel(all_questions, excel_path)


if __name__ == '__main__':
    '''
    1.需要将选项和题干在同一行的处理:
    查看，区分大小写：(.+)A\. 
    替换：$1\nA.
    
    2. 删除：华为考试交流群：281185682
    3. QUSTION xx与上一题在同一行：
    查看，区分大小写：(.+)(QUESTION (\d+))
    替换：$1\n$2
    4. 答案不在一行内
    查找：Correct Answer:\S*$
    替换：需要手动操作
    5. 答案与选项在一行内
    查找：(\S+)Correct Answer(.*)
    替换：$1\nCorrect Answer$2
    '''
    # txt_path, output_path = get_args()
    # import numpy as np
    # frame = pd.DataFrame(np.random.random((4, 4)),
    #              # index=['exp1', 'exp2', 'exp3', 'exp4'],
    #              columns=['jan2015', 'Fab2015', 'Mar2015', 'Apr2005'])
    #
    # # print(str(frame))
    # xl_writer = pd.ExcelWriter("data2.xlsx", engine='xlsxwriter')
    # frame.to_excel(xl_writer, index=False)  # 写到文件中

    try:
        parse_questions("H12-261 451题-已解锁.txt", r"H12-261 451题-已解锁.xlsx", 451, "华为,H12")
        parse_questions("华为H12-261 HCIE-RS题库.txt", r"华为H12-261 HCIE-RS题库.xlsx", 261, "华为,H12,HCIE-RS")
    except Exception as e:
        print(str(e))
        raise
