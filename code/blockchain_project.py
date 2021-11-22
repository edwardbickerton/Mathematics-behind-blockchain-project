#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 13:30:52 2021

"""
from hashlib import sha3_256
from binarytree import build2
from random import SystemRandom
import timeit


class Hashing:
    def my_hash_decimal(string: str) -> str:
        max_len = len(str(2**256-1))
        hash_int_string = str(int(sha3_256(string.encode()).hexdigest(), 16))
        num_leading_zeros = max_len - len(hash_int_string)
        return ''.join(['0' for i in range(num_leading_zeros)]) \
            + hash_int_string

    def my_hash_bin(string: str) -> str:
        max_len = 256
        hash_string = (
            str(bin(int(sha3_256(string.encode()).hexdigest(), 16))[2:]))
        num_leading_zeros = max_len - len(hash_string)
        return ''.join(['0' for i in range(num_leading_zeros)]) \
            + hash_string

    def my_hash_hex(string: str) -> str:
        max_len = 64
        hash_string = str(sha3_256(string.encode()).hexdigest())
        num_leading_zeros = max_len - len(hash_string)
        return ''.join(['0' for i in range(num_leading_zeros)]) \
            + hash_string

    def my_hash_short(string: str) -> str:
        return Hashing.my_hash_decimal(string)[:2**3]

    def test_hash_function(
            hash_function,
            num_trials: int = 10**6,
            correct_length: int = None,
            verbose: bool = True) -> bool:
        all_start_with_zero = True
        hash_list = []
        if verbose:
            incorrect_len_msg = (
                'ERROR: {0} of {1} is {2} digits long, it should be {3} '
                'digits.')
            all_start_with_zero_msg = (
                'WARNING: All trials started with a zero. Perhaps too much '
                'padding was added in {}.')
            hash_collisions_msg = (
                'WARNING: {0} hash collisions in {1} trials.')
            hash_collision_msg = (
                'WARNING: {0} inputs out of {1} went to {2}')
            test_passed_msg = 'All tests passed for {0}.'
        for i in range(num_trials):
            random_num_string = str(SystemRandom().getrandbits(256))
            hash_trial = hash_function(random_num_string)
            hash_list.append(hash_trial)
            if correct_length is not None:
                if len(hash_trial) != correct_length:
                    if verbose:
                        print(incorrect_len_msg.format(
                            hash_function,
                            random_num_string,
                            len(hash_trial),
                            correct_length))
                    return False
            if hash_trial[0] != '0':
                all_start_with_zero = False
        if all_start_with_zero:
            if verbose:
                print(all_start_with_zero_msg.format(hash_function))
            return False
        hash_collisions = 0
        hash_dict = {}
        for i in hash_list:
            hash_dict[i] = 0
        for i in hash_list:
            if i in hash_dict:
                hash_dict[i] += 1
        for i in hash_dict:
            if hash_dict[i] != 1:
                hash_collisions += 1
                if hash_dict[i] > 3:
                    if verbose:
                        print(hash_collision_msg.format(
                            hash_dict[i], num_trials, i))
        if hash_collisions != 0:
            if verbose:
                print(hash_collisions_msg.format(hash_collisions, num_trials))
            return False
        if verbose:
            print(test_passed_msg.format(hash_function))
        return True


class Merkle_Tree:
    def get_next_level(
            level: list,
            hash_function=Hashing.my_hash_short) -> list:
        if len(level) % 2 != 0:
            level.append(None)
        next_level = []
        i = 0
        while 2*i+1 < len(level):
            if level[2*i+1] is None:
                next_level.append(level[2*i])
            else:
                next_level.append(hash_function(level[2*i] + level[2*i+1]))
            i += 1
        return next_level

    def __init__(self,
                 data: list,
                 hash_function=Hashing.my_hash_short):
        self.data = data
        self.lists = [[hash_function(data_piece) for data_piece in data]]
        while len(self.lists[-1]) > 1:
            self.lists.append(
                Merkle_Tree.get_next_level(self.lists[-1]))
        self.root = self.lists[-1][0]
        lst = []
        for i in range(1, len(self.lists)+1):
            lst += self.lists[-i]
        values = []
        for value in lst:
            if value is None:
                values.append(value)
            else:
                values.append(int(value))
        self.tree = build2(values)

    def __str__(self):
        data = ''
        for i in range(len(self.data)):
            data += "\n{}. '{}'".format(i, self.data[i])
        return '{0}\nDATA:{1}'.format(self.tree, data)

    def Hash(input1, input2=None):
        if type(input1) == str:
            return int(Hashing.my_hash_short(input1))
        if type(input1) == type(input2) == int:
            pad1 = 2**3 - len(str(input1))
            pad2 = 2**3 - len(str(input2))
            return int(Hashing.my_hash_short(
                ''.join(['0' for i in range(pad1)])
                + str(input1)
                + ''.join(['0' for i in range(pad2)])
                + str(input2)))

    def verify(self, string: str, verbose: bool = True) -> list:
        if string not in self.data:
            if verbose:
                print("'{}' is not part of this Merkle tree.".format(string))
            return None
        instructions = []
        pos = self.data.index(string)
        for lst in self.lists:
            if len(lst) == 1:
                break
            if pos % 2 == 0 and lst[pos+1] is not None:
                instructions.append(('H', int(lst[pos+1])))
            elif pos % 2 == 1:
                instructions.append((int(lst[pos-1]), 'H'))
            pos = pos//2
        if verbose:
            print(instructions)
        return instructions


class Hashcash_Message:
    default_difficulty = 5

    def format_hashcash_message(hashcash_message):
        return ('Recipient: ' + hashcash_message.recipient
                + '\nNonce: ' + str(hashcash_message.nonce)
                + '\nMessage:\n' + hashcash_message.message)

    def __init__(self,
                 recipient: str,
                 message: str,
                 difficulty: int,
                 verbose: bool = False):

        self.message = message
        self.recipient = recipient
        if verbose:
            num_attempts_msg = (
                'It took {0} attempts to find a valid nonce:\n')
        attempts = 0
        while True:
            self.nonce = SystemRandom().getrandbits(256)
            trial_hash = Hashing.my_hash(
                Hashcash_Message.format_hashcash_message(self))
            if trial_hash[:difficulty] == ''.join(
                    ['0' for i in range(difficulty)]):
                if verbose:
                    print(num_attempts_msg.format(attempts))
                return
            attempts += 1

    def __str__(self):
        return Hashcash_Message.format_hashcash_message(self)

    def verify_proof_of_work(
            recipient: str,
            nonce: str,
            message: str,
            verbose: bool = True) -> str:
        difficulty = 0
        hash_to_verify = Hashing.my_hash('Recipient: ' + recipient
                                         + '\nNonce: ' + str(nonce)
                                         + '\nMessage:\n' + message)
        if verbose:
            no_work_msg = (
                'WARNING: No work done. This could be spam. The hash is:\n{}')
            low_difficulty_msg = (
                'WARNING: Low difficulty. Valid proof of work with difficulty '
                'only {0}. This could be spam. The hash is:\n{1}')
            valid_proof_msg = (
                'Valid proof of work with difficulty {0}, the hash is:\n{1}')
        for i in range(len(str(2**256-1))):
            if hash_to_verify[i] == '0':
                difficulty += 1
            else:
                if difficulty < 3:
                    if verbose:
                        print(no_work_msg.format(hash_to_verify))
                    return False
                if difficulty < 4:
                    if verbose:
                        print(low_difficulty_msg.format(
                            difficulty,
                            hash_to_verify))
                    return False
                if verbose:
                    print(valid_proof_msg.format(
                        difficulty,
                        hash_to_verify))
                return True

    def find_appropriat_difficulty(
            target_seconds: int = 2,
            trials: int = 10,
            verbose: bool = True):
        recipient = 'cypherpunk@recipient.com'
        if verbose:
            msg = (
                'A difficulty of {0} should require at least {1} seconds '
                'of work from this computer.')
        difficulty = 1
        while True:
            message = str(SystemRandom().getrandbits(1000))

            def wrapped_function():
                return Hashcash_Message(recipient, message, difficulty)
            time_taken = timeit.timeit(wrapped_function,
                                       number=trials) / trials
            if time_taken >= target_seconds:
                if verbose:
                    print(msg.format(
                        difficulty,
                        target_seconds))
                return difficulty
            difficulty += 1

    def example(appropriat_difficulty: int = default_difficulty) -> None:
        recipients = [
            'Timothy C.May',
            'Eric Hughes',
            'Satoshi Nakamoto']
        messages = [
            ("I've been working on a new electronic cash system that's fully "
             "peer-to-peer, with no trusted third party."),
            ("A specter is haunting the modern world, the specter of crypto "
             "anarchy."),
            ("Privacy is the power to selectively reveal oneself to the "
             "world.")]

        i = SystemRandom().getrandbits(1000) % len(messages)
        test = Hashcash_Message(
            recipients[i % len(recipients)],
            messages[i],
            appropriat_difficulty,
            verbose=True)
        print(str(test) + '\n\nCHECKING PROOF OF WORK DONE:')
        if not Hashcash_Message.verify_proof_of_work(
                test.recipient,
                test.nonce,
                test.message):
            print(
                'ERROR: test hashcash message:\n\n{}\n\nhas invalid proof of '
                'work.'.format(test))

    def test_verify_pow(
            appropriat_difficulty: int = default_difficulty,
            trials: int = 10,
            verbose: bool = True):
        if verbose:
            error_msg = (
                'ERROR: test hashcash message:\n\n{}\n\nhas invalid proof of '
                'work.')
            test_fail_msg = (
                'Function verify_proof_of_work failed a trial.')
            test_passed_msg = (
                'All tests passed for function verify_proof_of_work.')
        for i in range(trials):
            recipient = 'test@recipient.com'
            message = str(SystemRandom().getrandbits(10000))
            hashcash_message = Hashcash_Message(
                recipient,
                message,
                appropriat_difficulty)
            if not Hashcash_Message.verify_proof_of_work(
                    hashcash_message.recipient,
                    hashcash_message.nonce,
                    hashcash_message.message,
                    verbose=False):
                if verbose:
                    print(error_msg.format(hashcash_message))
                    print(test_fail_msg)
                return False
        if verbose:
            print(test_passed_msg)
        return True


def main():
    print()
    Hashing.test_hash_function(
        Hashing.my_hash,
        correct_length=len(str(2**256-1)))
    Hashcash_Message.default_difficulty = (
        Hashcash_Message.find_appropriat_difficulty())
    print('\nEXAMPLE:\n')
    Hashcash_Message.example()
    print()
    Hashcash_Message.test_verify_pow()
