import os
import re
import argparse


REGEX_RIGHT = re.compile(r'right\s*\((.+)\)', re.I)


def func_right(expression, context):

    exp = REGEX_RIGHT.search(expression.strip())
    if exp:

        print('found RIGHT STATEMENT: {}'.format(expression))
        left, right = exp.group(1).split(",")

        if not left.strip() in context:
            value = input('Please enter value for {}: '.format(left.strip()))
            context[left.strip()] = value

        return True, right.strip() == context[left.strip()][0:int(right.strip())]

    return False, None


class Statement:
    REGEX_IF = re.compile(r'if\s+(.*\s*=\s*.*)\s+then', re.I)
    REGEX_THEN = re.compile(r'then\s+(.*\s*=\s*.*);.*$', re.I)

    def __init__(self, input_text, line_num):
        self.input_text = input_text
        self.line_num = line_num

        self.if_expression = ''
        self.then_expression = ''

        self.funcs = [func_right, ]

        rslt = self.REGEX_IF.search(input_text)
        if rslt:
            self.if_expression = rslt.group(1).strip()

        rslt = self.REGEX_THEN.search(input_text)
        if rslt:
            self.then_expression = rslt.group(1).strip()

    def should_true(self, context):
        if not self.if_expression:
            return False

        parts = self.if_expression.split('=')
        if parts[1].strip() in context:
            return context[parts[0].strip()] == parts[1].strip()
        return False

    def __execute_then(self, context):
        print('trying then expression of {}'.format(self.input_text))
        if self.then_expression:
            
            left, right = self.then_expression.split('=')
            context[left.strip()] = right.strip()

    def execute(self, context):
        left, right = self.if_expression.split('=')
        check_value = None

        for func in self.funcs:
            has_value, check_value = func(self.if_expression, context)

        if has_value and check_value:
            print('im calling  function')
            self.__execute_then(context)
            return

        if not has_value:
            if not left.strip() in context:
                value = input('Please enter value for {}: '.format(left.strip()))
                context[left.strip()] = value

            print('Comparing {} == {}'.format(context[left.strip()], right.strip()))
            if context[left.strip()] == right.strip():
                self.__execute_then(context)

    def __str__(self):
        return '{}] {}\n\tif: {}\n\tthen: {}'.format(self.line_num, self.input_text, self.if_expression, self.then_expression)


def read_file(filename, context):
    rgx_begin = re.compile(r'^BEGIN$')

    begin = False

    print('reading {}'.format(filename))
    with open(filename, 'rt') as fp:
        for idx, line in enumerate(fp.readlines()):
            #print('processing line {}'.format(line))
            line = line.strip()
            if line.upper().startswith('IF'):
                if begin:
                    if statement.should_true(context):
                        yield Statement(line, idx)
                        begin = False
                else:
                    statement = Statement(line, idx)
                    yield statement
                    begin = False
            elif rgx_begin.search(line):
                begin = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=str)
    args = parser.parse_args()

    assert os.path.exists(args.root)
    for root, dirs, files in os.walk(args.root):
        for f in files:

            filename = os.path.join(root, f)
            context = dict()
            statements = read_file(filename, context)
            for statement in statements:
                statement.execute(context)
            print(context)
