from walmart_returns import Solver, full_store_list, save_model, update_store_data
import pandas as pd


if __name__ == '__main__':

    solver = Solver(50,1000)
    solver.run_v2()
    save_model(solver)

    #Exporting the data to a csv file
    cluster_exports = []
    for i,cluster in enumerate(solver.clusters):
        if len(cluster.all_stores_in_cluster) > 1:
            exports = cluster.cluster_export()
            cluster_exports.append(exports)

    data_frame = pd.DataFrame(cluster_exports)
    data_frame.to_csv('results_optimized_stores.csv', index=False)

    print('Done')

    save_model(solver)

