from trip_resolver import TripResolver

def main():
    trip_resolver = TripResolver()
    
    # Exemple de phrase d'entrée
    sentence = "Je veux voyager de Paris à Lyon"

    # Résoudre le voyage
    result = trip_resolver.resolve_trip(sentence)
    print(result)


if __name__ == "__main__":
    main()
