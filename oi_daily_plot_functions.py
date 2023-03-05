import numpy as np
import numpy.random as rd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg') 

from math import floor

dataset_names = [
    "domsub",
    "chaos",
    "driving",
    "bullying",
    "introversion",
    "amongus",
    "vibes",
    "math",
    "parenting",
    "animals",
    "theft",
    "age",
    "thinking",
    "emotions",
    "sleep",
]

possible_datasets = {
    "domsub": ["Sub", "Dom"],
    "chaos": ["Lawful", "Chaotic"],
    "driving": ["Bad driver", "Good driver"],
    "bullying": ["Bullied", "Bully"],
    "introversion": ["Extrovert", "Introvert"],
    "amongus": ["Impostor", "Crewmate"],
    "vibes": ["Chill", "Pretentious"],
    "math": ["Bad at math", "Good at math"],
    "parenting": ["Would kill their child", "Great parent"],
    "animals": ["Reminiscent of a raccoon", "Reminiscent of a hamster"],
    "theft": ["Would get burgled", "Potential burglar"],
    "age": ["Young at heart", "Old soul"],
    "thinking": ["Underthinks", "Overthinks"],
    "emotions": ["Emotionless", "Has emotions"],
    "sleep": ["Sleepy", "Awake"],
}

possible_answers = {
    "Q1": ["1", "2", "3", "4", "5"],
    "Q2": [
        "Being in a Ratatouille situation",
        "Public speaking",
        "Spiders",
        "Failure",
        "Your own emotions",
        "Me (Rose)",
    ],
    "Q3": [
        "Less than 10 minutes",
        "10-30 minutes",
        "30-90 minutes",
        "More than 90 minutes",
        "I don't get up in the morning",
    ],
    "Q4": ["Yes", "No"],
    "Q5": ["Red Bull", "Gatorade"],
    "Q6": ["Dan", "Ishaan (nano)", "Grey", "Bisman", "Zenghao"],
    "Q7": ["Salt", "Pepper (I'm a snail and I'm scared of salt"],
    "Q8": ["Yes", "No", "I've stolen, but not from a store"],
    "Q9": ["Ice cream", "Ice cube", "Snow cone", "Iced coffee", "Iced tea"],
    "Q10": ["Waterboarding", "Being forced to list nice things about yourself"],
    "Q11": ["Red", "Orange", "Yellow", "Green", "Blue", "Purple", "Pink"],
    "Q12": ["Yes", "No"],
    "Q13": ["1", "2", "3", "4", "5"],
    "Q14": ["One bug", "Twenty bugs"],
    "Q15": ["A bean", "A crumb from some kind of pastry", "A shrimp", "Grated cheese"],
    "Q16": ["I barely know her", "I hardly know her"],
    "Q17": ["1", "2", "3", "4", "5"],
    "Q18": ["Hat", "Shoes"],
    "Q19": [
        "Leader",
        "Just a guy who beats people up",
        "The coward",
        "The snack-bringer",
        "Double agent",
    ],
    "Q20": [
        "University residence cafeteria",
        "Back of the fridge",
        "Swamp",
        "Garbage",
        "Toilet",
    ],
    "Q21": ["Air", "Earth", "Water", "Fire", "Hydrogen"],
    "Q22": ["Truth", "Dare"],
    "Q23": [
        "Just the one sock would provide enough information",
        "2 socks",
        "3-5 socks",
        "More than 5 socks",
    ],
    "Q24": [
        "I would wear a pair of socks anyway",
        "I would wash a pair of socks, then wear them",
        "I would simply go without socks",
    ],
    "Q25": ["Gay or bi", "Other"],
    "Q26": ["Woman", "Other"],
    "Q27": ["Fast", "Slow"],
    "Q28": ["Yes", "No"],
    "Q29": [
        "< 2 minutes",
        "2-3 minutes",
        "3-10 minutes",
        "More than 10 minutes",
        "I forgot to set a timer/I left partway through",
    ],
}


def parse_csv(filename):

    text = np.transpose(
        np.genfromtxt(
            filename, dtype=str, delimiter="\t", skip_header=1, usecols=range(1, 31)
        )
    )
    (
        names,
        Q1,
        Q2,
        Q3,
        Q4,
        Q5,
        Q6,
        Q7,
        Q8,
        Q9,
        Q10,
        Q11,
        Q12,
        Q13,
        Q14,
        Q15,
        Q16,
        Q17,
        Q18,
        Q19,
        Q20,
        Q21,
        Q22,
        Q23,
        Q24,
        Q25,
        Q26,
        Q27,
        Q28,
        Q29,
    ) = text
    answers = {
        "Q1": Q1,
        "Q2": Q2,
        "Q3": Q3,
        "Q4": Q4,
        "Q5": Q5,
        "Q6": Q6,
        "Q7": Q7,
        "Q8": Q8,
        "Q9": Q9,
        "Q10": Q10,
        "Q11": Q11,
        "Q12": Q12,
        "Q13": Q13,
        "Q14": Q14,
        "Q15": Q15,
        "Q16": Q16,
        "Q17": Q17,
        "Q18": Q18,
        "Q19": Q19,
        "Q20": Q20,
        "Q21": Q21,
        "Q22": Q22,
        "Q23": Q23,
        "Q24": Q24,
        "Q25": Q25,
        "Q26": Q26,
        "Q27": Q27,
        "Q28": Q28,
        "Q29": Q29,
    }

    colours = []

    for i in range(len(names)):

        if Q11[i] == "Green":
            colour = "green"
        elif Q11[i] == "Red":
            colour = "r"
        elif Q11[i] == "Orange":
            colour = "orange"
        elif Q11[i] == "Yellow":
            colour == "yellow"
        elif Q11[i] == "Blue":
            colour = "b"
        elif Q11[i] == "Purple":
            colour = "darkviolet"
        elif Q11[i] == "Pink":
            colour = "hotpink"

        colours.append(colour)

    return names, colours, answers


def generate_datasets():

    dataset_name1, dataset_name2 = "", ""

    while dataset_name1 == dataset_name2:

        random1, random2 = rd.rand(), rd.rand()
        random1 *= len(possible_datasets)
        random2 *= len(possible_datasets)

        dataset_name1, dataset_name2 = (
            dataset_names[floor(random1)],
            dataset_names[floor(random2)],
        )

    return dataset_name1, dataset_name2


def get_axis_labels(dataset):

    axes = [possible_datasets[dataset][0], possible_datasets[dataset][1]]
    return axes


def compute_locs(bias_filename, dataset, names, answers):

    bias_info = np.transpose(
        np.genfromtxt(
            bias_filename,
            dtype=str,
            delimiter="\t",
            skip_header=1,
            usecols=range(0, 16),
        )
    )
    names, B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, B11, B12, B13, B14, B15 = bias_info

    if dataset == "domsub":
        bias = B1
        bias_weight = 0.7
        rel_Qs = ["Q1", "Q5", "Q13", "Q15", "Q18", "Q19", "Q22", "Q28"]
        Q_biases = {
            "Q1": [1, 0.75, 0.5, 0.25, 0],
            "Q5": [1, 0],
            "Q13": [1, 0.75, 0.5, 0.25, 0],
            "Q15": [0.5, 0, 0.7, 1],
            "Q18": [1, 0],
            "Q19": [1, 0.9, 0, 0.1, 0.5],
            "Q22": [1, 0],
            "Q28": [1, 0],
        }
        Q_rel_weights = {
            "Q1": 0.4,
            "Q5": 0.1,
            "Q13": 0.1,
            "Q15": 0.05,
            "Q18": 0.05,
            "Q19": 0.1,
            "Q22": 0.1,
            "Q28": 0.1,
        }

    elif dataset == "chaos":
        bias = B2
        bias_weight = 0.9
        rel_Qs = [
            "Q2",
            "Q7",
            "Q8",
            "Q9",
            "Q14",
            "Q16",
            "Q18",
            "Q20",
            "Q21",
            "Q22",
            "Q29",
        ]
        Q_biases = {
            "Q2": [1, 0.1, 0.1, 0.1, 0.1, 0],
            "Q7": [0, 1],
            "Q8": [1, 0, 0.7],
            "Q9": [0, 0, 0, 0, 1],
            "Q14": [1, 0],
            "Q16": [0, 1],
            "Q18": [1, 0],
            "Q20": [0, 0, 1, 1, 1],
            "Q21": [1, 1, 1, 1, 0],
            "Q22": [0, 1],
            "Q29": [1, 0.1, 0.1, 0, 1],
        }
        Q_rel_weights = {
            "Q2": 0.05,
            "Q7": 0.05,
            "Q8": 0.1,
            "Q9": 0.05,
            "Q14": 0.2,
            "Q16": 0.05,
            "Q18": 0.05,
            "Q20": 0.1,
            "Q21": 0.05,
            "Q22": 0.25,
            "Q29": 0.05,
        }

    elif dataset == "driving":
        bias = B3
        bias_weight = 0.5
        rel_Qs = ["Q4", "Q12", "Q25"]
        Q_biases = {"Q4": [1, 0], "Q12": [0.4, 0.6], "Q25": [0, 1]}
        Q_rel_weights = {"Q4": 0.45, "Q12": 0.05, "Q25": 0.5}

    elif dataset == "bullying":
        bias = B4
        bias_weight = 0.9
        rel_Qs = ["Q2", "Q5", "Q6", "Q10", "Q13", "Q19"]
        Q_biases = {
            "Q2": [0, 0.5, 0.5, 0.5, 1, 0],
            "Q5": [1, 0],
            "Q6": [0, 0.25, 0.5, 0.75, 1],
            "Q10": [1, 0],
            "Q13": [0, 0.25, 0.5, 0.75, 1],
            "Q19": [0.8, 1, 0, 0.5, 0.5],
        }
        Q_rel_weights = {
            "Q2": 0.3,
            "Q5": 0.05,
            "Q6": 0.2,
            "Q10": 0.05,
            "Q13": 0.2,
            "Q19": 0.2,
        }

    elif dataset == "introversion":
        bias = B5
        bias_weight = 0.7
        rel_Qs = ["Q2", "Q17"]
        Q_biases = {"Q2": [1, 0, 0.5, 0.5, 0, 1], "Q17": [1, 0.75, 0.5, 0.25, 0]}
        Q_rel_weights = {"Q2": 0.1, "Q17": 0.9}

    elif dataset == "amongus":
        bias = B6
        bias_weight = 0.7
        rel_Qs = ["Q8", "Q11", "Q19"]
        Q_biases = {
            "Q8": [0, 1, 0],
            "Q11": [0, 1, 1, 1, 1, 1, 1],
            "Q19": [1, 1, 1, 1, 0],
        }
        Q_rel_weights = {"Q8": 0.1, "Q11": 0.4, "Q19": 0.5}

    elif dataset == "vibes":
        bias = B7
        bias_weight = 0.7
        rel_Qs = ["Q2", "Q3", "Q5", "Q19", "Q28"]
        Q_biases = {
            "Q2": [0, 1, 0, 1, 0, 0],
            "Q3": [0.25, 0.5, 0.75, 1, 0],
            "Q5": [0, 1],
            "Q19": [1, 0, 0.5, 0, 1],
            "Q28": [1, 0],
        }
        Q_rel_weights = {"Q2": 0.1, "Q3": 0.2, "Q5": 0.1, "Q19": 0.2, "Q28": 0.4}

    elif dataset == "math":
        bias = B8
        bias_weight = 0.7
        rel_Qs = ["Q25"]
        Q_biases = {"Q25": [0, 1]}
        Q_rel_weights = {"Q25": 1}

    elif dataset == "parenting":
        bias = B9
        bias_weight = 0.7
        rel_Qs = ["Q1", "Q4", "Q9", "Q13", "Q23", "Q24"]
        Q_biases = {
            "Q1": [1, 0.75, 0.5, 0.25, 0],
            "Q4": [1, 0],
            "Q9": [0, 0, 0, 1, 1],
            "Q13": [0, 0.25, 0.5, 0.75, 1],
            "Q23": [1, 0.7, 0.3, 0],
            "Q24": [0, 1, 0],
        }
        Q_rel_weights = {
            "Q1": 0.05,
            "Q4": 0.15,
            "Q9": 0.05,
            "Q13": 0.15,
            "Q23": 0.3,
            "Q24": 0.3,
        }

    elif dataset == "animals":
        bias = B10
        bias_weight = 0.6
        rel_Qs = ["Q20"]
        Q_biases = {"Q20": [1, 0.75, 0.5, 0.25, 0]}
        Q_rel_weights = {"Q20": 1}

    elif dataset == "theft":
        bias = B11
        bias_weight = 0.4
        rel_Qs = ["Q6", "Q8", "Q13"]
        Q_biases = {
            "Q6": [0, 0.25, 0.5, 0.75, 1],
            "Q8": [0.9, 0, 1],
            "Q13": [0, 0.25, 0.5, 0.75, 1],
        }
        Q_rel_weights = {"Q6": 0.2, "Q8": 0.7, "Q13": 0.1}

    elif dataset == "age":
        bias = B12
        bias_weight = 0.9
        rel_Qs = ["Q2", "Q4", "Q9", "Q17", "Q22"]
        Q_biases = {
            "Q2": [0, 1, 1, 1, 1, 1],
            "Q4": [1, 0],
            "Q9": [0.1, 0.5, 0, 1, 1],
            "Q17": [1, 0.75, 0.5, 0.25, 0],
            "Q22": [1, 0],
        }
        Q_rel_weights = {"Q2": 0.2, "Q4": 0.2, "Q9": 0.1, "Q17": 0.2, "Q22": 0.3}

    elif dataset == "thinking":
        bias = B13
        bias_weight = 0.7
        rel_Qs = ["Q23", "Q29"]
        Q_biases = {"Q23": [0, 0.5, 0.75, 1], "Q29": [0, 0.5, 0.5, 1, 0]}
        Q_rel_weights = {"Q23": 0.3, "Q29": 0.7}

    elif dataset == "emotions":
        bias = B14
        bias_weight = 0.9
        rel_Qs = ["Q2", "Q10"]
        Q_biases = {"Q2": [0, 1, 0, 1, 1, 0], "Q10": [0, 1]}
        Q_rel_weights = {"Q2": 0.7, "Q10": 0.3}

    elif dataset == "sleep":
        bias = B15
        bias_weight = 0.8
        rel_Qs = ["Q3", "Q5"]
        Q_biases = {"Q3": [0.1, 1, 1, 1, 0], "Q5": [0.9, 0.1]}
        Q_rel_weights = {"Q3": 0.5, "Q5": 0.5}

    total_q_weights = 1 - bias_weight

    locations = np.zeros((len(names)))

    for i in range(len(names)):

        biased_val_i = float(bias[i])

        location = bias_weight * biased_val_i

        for Q in rel_Qs:

            response = answers[Q][i]
            Q_bias = Q_biases[Q]
            Q_weight = Q_rel_weights[Q] * total_q_weights

            j = 0
            for answer in possible_answers[Q]:

                if response == answer:

                    q_val = Q_bias[j]
                    break

                j += 1

            location += Q_weight * q_val

        location = 2 * location - 1  # Map to [-1, 1] interval
        locations[i] = location
    print(locations)
    return locations


def create_plot(names, colours, dataset1, dataset2, axes1, axes2):

    neg_axis1, pos_axis1 = axes1[0], axes1[1]
    neg_axis2, pos_axis2 = axes2[0], axes2[1]

    X = dataset1
    Y = dataset2

    matplotlib.rcParams.update(matplotlib.rcParamsDefault)

    fig, ax = plt.subplots()
    plt.axvline(color="k")
    plt.axhline(color="k")

    for i in range(len(names)):

        name = names[i]
        X_val, Y_val = X[i], Y[i]
        colour = colours[i]
        plt.scatter(X_val, Y_val, color=colour)
        plt.annotate(name, (X_val, Y_val), color="k", fontsize=8)

    plt.xlim(-1, 1)
    plt.ylim(-1, 1)
    plt.xticks([])
    plt.yticks([])
    ax.set_xlabel(neg_axis2)
    ax.set_ylabel(neg_axis1, rotation=0)
    ax2 = ax.twiny()
    ax2.plot()
    ax2.set_xlabel(pos_axis2)
    plt.xticks([])
    ax3 = ax.twinx()
    ax3.plot()
    ax3.set_ylabel(pos_axis1, rotation=0)
    plt.yticks([])
    plt.tight_layout()
    plt.savefig("dailygraph.png")


def make_daily_graph(filename, bias_filename):

    names, colours, answers = parse_csv(filename)

    dataset1, dataset2 = generate_datasets()

    axes1, axes2 = get_axis_labels(dataset1), get_axis_labels(dataset2)

    coords1, coords2 = compute_locs(
        bias_filename, dataset1, names, answers
    ), compute_locs(bias_filename, dataset2, names, answers)

    create_plot(names, colours, coords1, coords2, axes1, axes2)
