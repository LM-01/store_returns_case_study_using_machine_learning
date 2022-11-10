from walmart_returns import Solver, full_store_list, save_model, update_store_data
import pandas as pd


if __name__ == '__main__':
    
    """Running the new process here.

    1.   Create new clusters and add stores based on the new requirements
    2.   run the optimzation path
    3.   save the file


    """

    solver = Solver(50,1000)
    solver.stores_list = full_store_list(solver)
    update_store_data(solver)
    solver.run_v2()
    save_model(solver)

    # Just exporting the data
    routes = []
    cluster_exports = []
    for i,cluster in enumerate(solver.clusters):
        if len(cluster.all_stores_in_cluster) > 1:
            exports = cluster.cluster_export()
            cluster_exports.append(exports)

    data_frame = pd.DataFrame(cluster_exports)
    data_frame.to_csv('results_optimized_stores.csv', index=False)

    print('Done')

    save_model()

