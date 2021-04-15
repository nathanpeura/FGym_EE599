
def check_vadd_vector(observation, b_vec, observed_result):
    expected_result = observation + b_vec

    # print("A: ", observation)
    # print("B: ", b_vec)
    # print("Res: ", observed_result)
    # print("Expected: ", expected_result)

    return observed_result == expected_result
