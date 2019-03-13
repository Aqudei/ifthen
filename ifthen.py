import os
import re
import argparse


class Statement:
    REGEX_IF = re.compile(r'if\s+(.*\s*=\s*.*)\s+then', re.I)
    REGEX_THEN = re.compile(r'then\s+(.*\s*=\s*.*);.*$', re.I)

    def __init__(self, input_text, line_num):
        self.input_text = input_text
        self.line_num = line_num

        self.if_expression = ''
        self.then_expression = ''

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

    def execute(self, context):
        left, right = self.if_expression.split('=')
        
        name, val = func_right(context)
        if name and val:
            pass

        if not left.strip() in context:
            value = input('Please enter value for {}'.format(left.strip()))
            context[left.strip()] = value
        
        if context[left.strip()] == right.strip():
            if self.then_expression:
                left, right = self.then_expression.split('=')
                context[left.strip()] = right.strip()

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
