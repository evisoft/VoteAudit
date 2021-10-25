#python 3
from itertools import permutations
import argparse
from argparse import RawTextHelpFormatter

import hmac
import hashlib

def audit(secrets, hashes, vote_options):
    if len(secrets) != len(hashes):
        raise Exception('Audit failed. Number of secrets must be equal with number of hashes.')

    if len(set(secrets)) != len(secrets):
        raise Exception('Audit failed. Duplicate detected in list of secrets.')

    hashes_set = set(hashes) #for faster checkup use set()
    if len(hashes_set) != len(hashes):
        raise Exception('Audit failed. Duplicate detected in list of hashes.')

    validated_vote_options = []
    for secret in secrets:
        for vote in vote_options:
            signature = hmac.new(bytes(secret , 'utf-8'), msg = bytes(vote , 'utf-8'), digestmod = hashlib.sha256).hexdigest() #<-- magic here
            if signature in hashes_set:
                validated_vote_options.append(vote)
                hashes_set.remove(signature) #remove to avoid count twice same hash
                continue #go the next secret, do not use same secret twice
    
    if len(hashes_set) != 0:
        raise Exception('Audit failed. Not all hashes match with signature or options votes combinations is incomplete.')

    if len(validated_vote_options) != len(hashes):
        raise Exception('Audit failed. Number of validated hashes not match with number of expressed votes.')

    return validated_vote_options

def arrangements(options, min_options = 1, max_options = 1):
    #total = options_len!/(options_len - min_options)! + options_len!/(options_len - max_options)!
    arr = []
    for i in range(min_options, max_options + 1):
        tuples = permutations(options, i)
        for t in tuples:            
            str = ','.join(t)
            arr.append(str)
    return arr

def compute_votes(valid_votes):
    results = {}
    for vote in valid_votes:
        split_options = vote.split(",")
        for option in split_options:
            if not option in results:
                results[option] = 1
            else:
                results[option] = results[option] + 1
    return results

def main():
    """The main function."""
    description = """This program is useful to audit hashes generated by voting server from VoteMe.App &
            To validate votes need to have file with secrets, file with hashes and file with valid voting options.            
            """
    # Parse CLI arguments
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('-s', '--secrets', help='Textual file with list of secrets.')
    parser.add_argument('-a', '--hashes', help='Textual file with list of hashes.')
    parser.add_argument('-o', '--options', help='Textul file with valid voting options.')
    parser.add_argument('-n','--min', type=int, default=1, help='Minimum candidates from voting options to pick.')
    parser.add_argument('-x', '--max', type=int, default=1, help='Maximum candidates from voting options to pick.')
    args = parser.parse_args()

    with open(args.secrets, 'r') as f:
        secrets = f.read().splitlines() 

    with open(args.hashes, 'r') as f:
        hashes = f.read().splitlines() 

    with open(args.options, 'r') as f:
        options = f.read().splitlines() 

    voting_arrangements = arrangements(options, args.min, args.max)
    valid_votes = audit(secrets, hashes, voting_arrangements)
    results = compute_votes(valid_votes)
    print(results)

if __name__ == '__main__':
    main()
