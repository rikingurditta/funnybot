import numpy as np
import numpy.random as rd
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")

from math import floor

dataset_names = [
    "animals",
    "nails",
    "phone",
    "babysitter",
    "pets",
    "division",
    "swimming",
    "temper",
    "bird",
    "wokeness",
    "movie",
    "type",
    "shape",
    "camping",
    "chadness",
    "body",
    "attraction",
    "afterlife",
    "drinks",
]

possible_datasets = {
    "animals": ["Reminiscent of a raccoon", "Reminiscent of a hamster"],
    "nails": ["Long nails", "Short nails"],
    "phone": ["Phone dead", "Phone charged"],
    "babysitter": ["Should be babysat", "Babysitter"],
    "pets": ["Dogs", "Cats"],
    "division": ["Can't do long division", "Can do it"],
    "swimming": ["Drowning", "Could be a lifeguard"],
    "temper": ["Short-tempered", "Patient"],
    "bird": ["Early bird", "Night owl"],
    "wokeness": ["Raciest", "Woke"],
    "movie": ["Dies first in horror movie", "Last one standing"],
    "type": ["Type A", "Type B"],
    "shape": ["Kiki", "Bouba"],
    "camping": ["Likes camping", "Hates camping"],
    "chadness": ["Virgin", "Chad"],
    "body": ["Helps you bury a body", "Rats you out"],
    "attraction": ["Boobs", "Ass"],
    "afterlife": ["Hellbound", "Heavenbound"],
    "drinks": ["Tea", "Coffee"],
}

possible_answers = {
    "Q1": ["Red", "Orange", "Yellow", "Green", "Blue", "Purple", "Pink"],
    "Q2": [
        "University residence cafeteria",
        "Back of the fridge",
        "Swamp",
        "Garbage",
        "Toilet",
        "",
    ],
    "Q3": ["Yes", "No", "I've stolen, but not from a store", ""],
    "Q4": ["Gay or bi", "Other", ""],
    "Q5": [
        "Aries (Mar 21 - Apr 19)",
        "Taurus (Apr 20 - May 20)",
        "Gemini (May 21 - Jun 20)",
        "Cancer (Jun 21 - Jul 22)",
        "Leo (Jul 23 - Aug 22)",
        "Virgo (Aug 23 - Sep 22)",
        "Libra (Sep 23 - Oct 22)",
        "Scorpio (Oct 23 - Nov 21)",
        "Sagittarius (Nov 22 - Dec 21)",
        "Capricorn (Dec 22 - Jan 19)",
        "Aquarius (Jan 20 - Feb 18)",
        "Pisces (Feb 19 - Mar 20)",
        "",
    ],
    "Q6": [
        "Berries",
        "Torus",
        "Gemstone",
        "Carcinoma",
        "Leg",
        "Virgin",
        "Libel",
        "Scrungle",
        "Sadge",
        "Cornchip",
        "Asparagus",
        "Piss",
        "",
    ],
    "Q7": ["Gay son", "Thot daughter", ""],
    "Q8": [
        "The oldest child",
        "The middle child/one of the middle childs",
        "The youngest child",
        "I don't have siblings",
        "",
    ],
    "Q9": [
        "Today",
        "This week",
        "Within the past month",
        "Over a month ago/don't remember",
        "",
    ],
    "Q10": [
        "A sentient vending machine",
        "A seven foot tall kindergartener",
        "I would not be able to take either of these",
        "",
    ],
    "Q11": ["Zayn", "Louis", "Harry", "Niall", "The other one", ""],
    "Q12": [
        "Be stabbed in the stomach",
        "Gnaw off your own leg to escape",
        "Be burned grievously",
        "Be left alone with your own thoughts for 5 hours",
        "",
    ],
    "Q13": ["None", "1 - 3", "4 - 7", "7 - 9", "10+", ""],
    "Q14": ["Just woke up", "Are still awake from the day before", ""],
    "Q15": [
        "Leave it alone and hope it goes away",
        "Trap it and bring it outside",
        "Run away and cede the location",
        "Squash it",
        "Kiss it",
        "",
    ],
    "Q16": ["Tim's", "Starbucks", ""],
    "Q17": [
        "A french press",
        "A children's dollhouse",
        "A coffee table",
        "A bookshelf",
        "A wardrobe",
        "A bed",
        "",
    ],
    "Q18": ["Reserved", "Outgoing", ""],
    "Q19": [
        "Not hungry - you want to get ahead of the hunger",
        "A little hungry",
        "Very hungry",
        "So hungry you're about to pass out",
        "",
    ],
    "Q20": [
        "Stress ball",
        "Toothbrush",
        "Lamp",
        "Hardcover book",
        "Rolling pin",
        "Frying pan",
        "Kitchen knife",
        "",
    ],
    "Q21": ["1", "2", "3", "4", "5", ""],
    "Q22": ["Sea urchin", "Blobfish", ""],
    "Q23": [
        "Very little/none",
        "I'll appreciate a pun if it's really clever",
        "Tolerance? I love puns!",
        "",
    ],
    "Q24": [
        "Me",
        "Someone else",
        "There's nothing to shovel (e.g. live in an apartment)",
        "",
    ],
    "Q25": [
        "Wade in slowly",
        "Jump in",
        "Go down a waterslide",
        "Dive in from the edge",
        "Dive in from a diving board",
        "",
    ],
    "Q26": ["Lola Bunny", "Jessica Rabbit", ""],
    "Q27": ["Book smart", "Street smart", ""],
    "Q28": [
        "Under a minute",
        "A couple minutes",
        "Quite a while",
        "I don't think I could do it",
        "",
    ],
    "Q29": [
        "When someone starts something and then doesnt fini",
        "When someone touches you without warning",
        "When someone is late",
        "When someone is mad at you for being late",
        "When someone is being stupid",
        "When you have to wait",
        "",
    ],
    "Q30": [
        "As a baby",
        "As a young child",
        "Elementary school",
        "Middle-high school",
        "University",
        "After university",
        "Still waiting",
        "",
    ],
    "Q31": ["1", "2", "3", "4", "5", ""],
    "Q32": ["Yes", "No", ""],
}


def parse_csv(filename):

    text = np.transpose(
        np.genfromtxt(
            filename, dtype=str, delimiter=",", skip_header=1, usecols=range(1, 34)
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
        Q30,
        Q31,
        Q32,
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
        "Q30": Q30,
        "Q31": Q31,
        "Q32": Q32,
    }

    colours = []

    for i in range(len(names)):

        if Q1[i] == "Green":
            colour = "green"
        elif Q1[i] == "Red":
            colour = "r"
        elif Q1[i] == "Orange":
            colour = "orange"
        elif Q1[i] == "Yellow":
            colour == "yellow"
        elif Q1[i] == "Blue":
            colour = "b"
        elif Q1[i] == "Purple":
            colour = "darkviolet"
        elif Q1[i] == "Pink":
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
            usecols=range(0, 20),
        )
    )
    (
        names,
        B1,
        B2,
        B3,
        B4,
        B5,
        B6,
        B7,
        B8,
        B9,
        B10,
        B11,
        B12,
        B13,
        B14,
        B15,
        B16,
        B17,
        B18,
        B19,
    ) = bias_info

    if dataset == "animals":
        bias = B1
        bias_weight = 0.6
        rel_Qs = ["Q2"]
        Q_biases = {"Q2": [1, 0.75, 0.5, 0.25, 0, 0.5]}
        Q_rel_weights = {"Q2": 1}

    elif dataset == "nails":
        bias = B2
        bias_weight = 0.7
        rel_Qs = ["Q28"]
        Q_biases = {"Q28": [0, 0.3, 0.7, 1, 0.5]}
        Q_rel_weights = {"Q28": 1}

    elif dataset == "phone":
        bias = B3
        bias_weight = 0.7
        rel_Qs = ["Q19"]
        Q_biases = {"Q19": [1, 0.7, 0.3, 0, 0.5]}
        Q_rel_weights = {"Q19": 1}

    elif dataset == "babysitter":
        bias = B4
        bias_weight = 0.9
        rel_Qs = ["Q8", "Q19"]
        Q_biases = {"Q8": [1, 1, 0, 0.5, 0.5], "Q19": [0.9, 1, 0.1, 0, 0.5]}
        Q_rel_weights = {"Q8": 0.8, "Q19": 0.2}

    elif dataset == "pets":
        bias = B5
        bias_weight = 0.8
        rel_Qs = ["Q7", "Q18"]
        Q_biases = {"Q7": [0, 1, 0.5], "Q18": [0, 1, 0.5]}
        Q_rel_weights = {"Q7": 0.2, "Q18": 0.8}

    elif dataset == "division":
        bias = B6
        bias_weight = 0.65
        rel_Qs = ["Q4", "Q32"]
        Q_biases = {"Q4": [0, 1, 0.5], "Q32": [1, 0, 0.5]}
        Q_rel_weights = {"Q4": 0.2, "Q32": 0.8}

    elif dataset == "swimming":
        bias = B7
        bias_weight = 0.6
        rel_Qs = ["Q25"]
        Q_biases = {"Q25": [0, 0.25, 0.5, 0.75, 1, 0.5]}
        Q_rel_weights = {"Q25": 1}

    elif dataset == "temper":
        bias = B8
        bias_weight = 0.8
        rel_Qs = ["Q9", "Q23"]
        Q_biases = {"Q9": [0, 0.3, 0.7, 1, 0.5], "Q23": [0, 0.5, 1, 0.5]}
        Q_rel_weights = {"Q9": 0.7, "Q23": 0.3}

    elif dataset == "bird":
        bias = B9
        bias_weight = 0.6
        rel_Qs = ["Q14"]
        Q_biases = {"Q14": [0, 1, 0.5]}
        Q_rel_weights = {"Q14": 1}

    elif dataset == "wokeness":
        bias = B10
        bias_weight = 0.6
        rel_Qs = ["Q13"]
        Q_biases = {"Q13": [0, 0.2, 0.3, 0.9, 1, 0.5]}
        Q_rel_weights = {"Q13": 1}

    elif dataset == "movie":
        bias = B11
        bias_weight = 0.9
        rel_Qs = ["Q27", "Q31"]
        Q_biases = {"Q27": [0, 1, 0.5], "Q31": [0, 0.25, 0.5, 0.75, 1, 0.5]}
        Q_rel_weights = {"Q27": 0.25, "Q31": 0.75}

    elif dataset == "type":
        bias = B12
        bias_weight = 1
        rel_Qs = []
        Q_biases = {}
        Q_rel_weights = {}

    elif dataset == "shape":
        bias = B13
        bias_weight = 0.8
        rel_Qs = ["Q22"]
        Q_biases = {"Q22": [0, 1, 0.5]}
        Q_rel_weights = {"Q22": 1}

    elif dataset == "camping":
        bias = B14
        bias_weight = 0.7
        rel_Qs = ["Q15", "Q17"]
        Q_biases = {
            "Q15": [0.9, 1, 0, 0.1, 1, 0.5],
            "Q17": [1, 0.9, 0.8, 0.2, 0, 0.1, 0.5],
        }
        Q_rel_weights = {"Q15": 0.7, "Q17": 0.3}

    elif dataset == "chadness":
        bias = B15
        bias_weight = 0.8
        rel_Qs = ["Q6", "Q30"]
        Q_biases = {
            "Q6": [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0.5],
            "Q30": [0, 0.1, 0.2, 0.3, 0.4, 0.5, 1, 0.5],
        }
        Q_rel_weights = {"Q6": 0.3, "Q30": 0.7}

    elif dataset == "body":
        bias = B16
        bias_weight = 0.5
        rel_Qs = ["Q3", "Q21", "Q24"]
        Q_biases = {
            "Q3": [0, 1, 0, 0.5],
            "Q21": [1, 0.75, 0.5, 0.25, 0, 0.5],
            "Q24": [0, 1, 0.5, 0.5],
        }
        Q_rel_weights = {"Q3": 0.4, "Q21": 0.3, "Q24": 0.3}

    elif dataset == "attraction":
        bias = B17
        bias_weight = 0.5
        rel_Qs = ["Q26"]
        Q_biases = {"Q26": [1, 0, 0.5]}
        Q_rel_weights = {"Q26": 1}

    elif dataset == "afterlife":
        bias = B18
        bias_weight = 0.5
        rel_Qs = ["Q3", "Q4"]
        Q_biases = {"Q3": [0, 1, 0, 0.5], "Q4": [0, 1, 0.5]}
        Q_rel_weights = {"Q3": 0.05, "Q4": 0.95}

    elif dataset == "drinks":
        bias = B19
        bias_weight = 0.8
        rel_Qs = ["Q16"]
        Q_biases = {"Q16": [0, 1, 0.5]}
        Q_rel_weights = {"Q16": 1}

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
            q_val = 0
            for answer in possible_answers[Q]:

                if response == answer:

                    q_val = Q_bias[j]
                    break

                j += 1

            location += Q_weight * q_val

        location = 2 * location - 1  # Map to [-1, 1] interval
        locations[i] = location

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
    plt.close()


def make_daily_graph(filename, bias_filename):

    names, colours, answers = parse_csv(filename)

    dataset1, dataset2 = generate_datasets()

    axes1, axes2 = get_axis_labels(dataset1), get_axis_labels(dataset2)

    coords1, coords2 = compute_locs(
        bias_filename, dataset1, names, answers
    ), compute_locs(bias_filename, dataset2, names, answers)

    create_plot(names, colours, coords1, coords2, axes1, axes2)
