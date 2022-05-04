import json
import ahpy


def parse_ahp_weights() : 
    try :
        with open('./files/ahp_weights.json', 'r') as f :
            return json.load(f)

    except FileNotFoundError as error :
        print(error)
        exit(1)


def apply_ahp(all_results) : 

    print('AHP')

    fixes = []

    for r in all_results : 

        path = tuple(r.items())[1][1]
        leaves = path[-1]

        if type(leaves) == list : 
            print('TODO')

        else : 
            
            leaf_type, leaf_value = get_leaf_type(NEO4J_ADDRESS, l)
            print(leaves)














    

    # experience_comparisons = {('Moll', 'Nell'): 1/4, ('Moll', 'Sue'): 4, ('Nell', 'Sue'): 9}
    # education_comparisons = {('Moll', 'Nell'): 3, ('Moll', 'Sue'): 1/5, ('Nell', 'Sue'): 1/7}
    # charisma_comparisons = {('Moll', 'Nell'): 5, ('Moll', 'Sue'): 9, ('Nell', 'Sue'): 4}
    # age_comparisons = {('Moll', 'Nell'): 1/3, ('Moll', 'Sue'): 5, ('Nell', 'Sue'): 9}


    # ver_comparisons = {('path_0', 'path_1'): 0/0}
    # priv_comparisons = {('path_0', 'path_1'): 5/9}
    # root_comparisons = {('path_0', 'path_1'): 3/9}
    # cap_comparisons = {('path_0', 'path_1'): 4/9}
    # sysc_comparisons = {('path_0', 'path_1'): 3/9}
    # ro_fs_comparisons = {('path_0', 'path_1'): 3/9},
    # nn_priv_comparisons = {('path_0', 'path_1'): 3/9}
    # low_risk_comparisons = {('path_0', 'path_1'): 3/9}


    # criteria_comparisons = {('Experience', 'Education'): 4, ('Experience', 'Charisma'): 3, ('Experience', 'Age'): 7,
	# 		    ('Education', 'Charisma'): 1/3, ('Education', 'Age'): 3,
	# 		    ('Charisma', 'Age'): 5}

    # cri_comparisons = {('', ''): , ('', ''): , ('', ''): , ('', ''): , ('', ''): , ('', ''): , ('', ''):}


    # experience = ahpy.Compare('Experience', experience_comparisons, precision=3, random_index='saaty')
    # education = ahpy.Compare('Education', education_comparisons, precision=3, random_index='saaty')
    # charisma = ahpy.Compare('Charisma', charisma_comparisons, precision=3, random_index='saaty')
    # age = ahpy.Compare('Age', age_comparisons, precision=3, random_index='saaty')
    # criteria = ahpy.Compare('Criteria', criteria_comparisons, precision=3, random_index='saaty')

    # criteria.add_children([experience, education, charisma, age])

    # print(criteria.target_weights)



