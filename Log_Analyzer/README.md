# Log_Analyzer
1) This tool will predict the type of error comes in your logs.

2) It compairs the accuracy of different selection algorithms and
   give  you the best result among all algorithms with the best suited parameters.

RUN:-

if __name__ == "__main__":
    la = LogAnalyzer()
    x_train, x_test, y_train, y_test = la.return_stable_data_in_vectors()
    print(la.model_comparision(x_train, y_train))

run this code to get the results.

If want to test with new data, change the sample data file path in read_csv function.