#include <mlpack/methods/linear_regression/linear_regression.hpp>
using namespace mlpack::regression;

int main() {
    arma::mat data; // The dataset itself.
    arma::vec responses; // The responses, one row for each row in data.

    data.randn(2,2);
    responses.eye(2,2);

    LinearRegression lr(data, responses);
    arma::vec parameters = lr.Parameters();
}
