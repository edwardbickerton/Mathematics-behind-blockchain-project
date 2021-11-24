#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 19 13:56:41 2021

"""
from blockchain_project import Merkle_Tree
from random import randint

names = ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve', 'Frank', 'George', 'Harry',
         'Ian', 'James', 'Kacey', 'Laura', 'Macy', 'Natasha', 'Olaf', 'Pablo',
         'Quinn', 'Rupert', 'Simon', 'Tim']


def random_transaction():
    return '{0} sends {1} {2} BTC'.format(
        names[randint(0, len(names)-1)],
        names[randint(0, len(names)-1)],
        randint(1, 10))


def random_transactions(number: int = None):
    if number is None:
        number = randint(7,11)
    return (['Coinbase Transaction: 6.25 BTC to {}'.format(
        names[randint(0, len(names)-1)])]
            + [random_transaction() for i in range(number-1)])


def Hash(input1, input2=None):
    return Merkle_Tree.Hash(input1, input2)


def Verify(tree, string):
    instructions = tree.verify(string, verbose=False)
    if instructions is None:
        print("'{}' is not part of this Merkle tree.".format(string))
        return
    print("run:\nH = Hash('{}')".format(string))
    print('print(H)')
    for instruction in instructions:
        if instruction[0] == 'H':
            print('H = Hash(H, {})'.format(instruction[1]))
            print('print(H)')
        else:
            print('H = Hash({}, H)'.format(instruction[0]))
            print('print(H)')
    print('H == {}'.format(int(tree.root)))


def main():
    global transactions, tree
    transactions = random_transactions()
    print('transactions:')
    print(transactions)
    tree = Merkle_Tree(transactions)
    print('\ntree = Merkle_Tree(transactions):\n')
    print(tree)


if __name__ == '__main__':
    main()
