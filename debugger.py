from config import Settings
import pickle
import simulate

def neighbor_check(df, id1, id2):
    #Check if id2 is a neighbor of id2
    neighbors = df.at[id1, "neighbors"]
    neighbor_ids = [x["neighbor_id"] for x in neighbors]
    return id2 in neighbor_ids

def neighbor_validation(df):
    for id1 in df.index:
        neighbors = df.at[id1, "neighbors"]
        for neighbor in neighbors:
            id2 = neighbor["neighbor_id"]
            if not neighbor_check(df, id2, id1):
                print(f"{id2} is a neighbor of {id1} but {id1} is not a neighbor of {id2}")

if __name__ == "__main__":
    settings = Settings()
    settings.simulation_resolution = "county"
    initial_df = pickle.load(open("data-32.sim", "rb"))
    neighbor_validation(initial_df)
    simulation_data = simulate.run(initial_df, settings)