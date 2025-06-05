import json         ### AtomicCards.json is the data source
import argparse     ### Using argparse to parse options on the command line
import pdb          ### Debugger

### Define a CardFilter class to collect the logic for building and running a query.
###     To add a filter, update from_args(), then add an argument to the parser.


class CardFilter:
    def __init__(self, criteria):
        self.criteria = criteria if criteria else None

    @classmethod
    def from_args(cls, args):
        ### Build a list of criteria that can be called by the match() function
        ### This is better than using helper functions for (match) because
        ### it reduces the number of places that have to be updated for a
        ### new criterion, and it avoids using logic that isn't required.
        criteria = []

        ### Logic to test for required colors.
        ### We skip this if no colors are required.
        if args.colors_all:
            required_colors = set(args.colors_all)
            criteria.append(lambda face: set(args.colors_all) <= set(face['colors']))

        ### Logic to test for accepted colors.
        ### We skip this if no colors are specified (on the assumption all are accepted).
        if args.colors_only:
            accepted = set(args.colors_only)
            criteria.append(lambda face: set(face['colors']) <= accepted)
        
        ### Logic to test for power range
        ### We skip this if no power is specified.
        if args.power_min or args.power_max:
            def power_check(face):
                p = face.get('power')
                min = int(args.power_min) if args.power_min else None
                max = int(args.power_max) if args.power_max else None
                if not p or not p.isnumeric():
                    return False
                else:
                    return (min or 0) <= int(p) <= (max or 9999)
            criteria.append(power_check)

        ### Logic to test for toughness range.
        ### We skip this if no toughness is specified.
        if args.tough_min or args.tough_max:
            def toughness_check(face):
                t = face.get('toughness')
                min = int(args.tough_min) if args.tough_min else None
                max = int(args.tough_max) if args.tough_max else None
                if not t or not t.isnumeric():
                    return False
                else:
                    return (min or 0) <= int(t) <= (max or 9999) # I'll have to update this line and the corresponding one in the power function if a creature's base toughness ever goes over 9999.
            criteria.append(toughness_check)

        ### Logic to test for required types.
        ### We skip this if no types are required.
        if args.types_all:
            required = set(args.types_all)
            criteria.append(lambda face: required <= set(face['types']))

        ### Logic to test for accepted types.
        ### We skip this if no types are specified.
        if args.types_only:
            accepted = set(args.types_only)
            criteria.append(lambda face: set(face['types']) <= accepted)

        ### Logic to test for CMC range.
        ### We skip this if no CMC parameters are given
        if args.cmc_min or args.cmc_max:
            def cmc_check(face):
                cmc = face.get('convertedManaCost')
                min = float(args.cmc_min) if args.cmc_min else 0
                max = float(args.cmc_max) if args.cmc_max else 9999
                if not cmc:
                    return False
                else:
                    return(min <= cmc <= max)
            criteria.append(cmc_check)

        ### Create an instance of the CardFilter class with the criteria as an attribute
        return cls(criteria = criteria)

    def filter(self, card_dict):
        return {
            name: faces
            for name, faces in card_dict.items()
            if self.matches(faces)
        }

    def matches(self, faces):
        for face in faces:
            if self.match(face):
                return True
        else:
            return False
    
    def match(self, face):
        ### Return false if any one of the criteria fails.
        return not any(not criterion(face) for criterion in self.criteria)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--colors-only', nargs = "*", default = None,
                        help = 'Allowed colors (e.g., --colorsonly R G)')
    parser.add_argument('-C', '--colors-all', nargs = "*", default = None,
                        help = 'Required colors (e.g., --colors-all R G)')
    parser.add_argument('-p', '--power-min', type = int, default = None,
                        help = 'The minimum desired power value')
    parser.add_argument('-P', '--power-max', type = int, default = None,
                        help = 'The maximum desired power value')
    parser.add_argument('-g', '--tough-min', type = int, default = None,
                        help = 'The minimum desired toughness value')
    parser.add_argument('-G', '--tough-max', type = int, default = None,
                        help = 'The maximum desired toughness value')
    parser.add_argument('-t', '--types-only', nargs = "*", default = None,
                        help = 'Allowed types (e.g. --types only Artifact Enchantment)')
    parser.add_argument('-T', '--types-all', nargs = "*", default = None,
                        help = 'Required types (e.g., --types-all Enchantment Creature)')
    parser.add_argument('-m', '--cmc-min', type = int, default = None,
                        help = 'The minimum desired converted mana cost')
    parser.add_argument('-M', '--cmc-max', type = int, default = None,
                        help = 'The maximum desired converted mana cost')
    args = parser.parse_args()
    card_filter = CardFilter.from_args(args)

    with open('AtomicCards.json', 'r', encoding = 'UTF-8') as f:
        data = json.load(f)

    card_dict = data['data']

    filtered_cards = card_filter.filter(card_dict)
    for name, faces in filtered_cards.items():
        print(name)
        # for face in faces:
        #     print(face)


if __name__=='__main__':
    main()