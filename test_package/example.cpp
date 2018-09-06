#include <mlpack/methods/linear_regression/linear_regression.hpp>

using namespace mlpack::regression;

int main() {

    // Generate some data and response
    arma::mat data = arma::randn<arma::mat>(20, 2);
    arma::rowvec responses(20);

    // For this test the response will be perfect linear
    for(unsigned int i = 0; i < 20; i++) {
        responses(i) = arma::as_scalar(data.row(i) * arma::vec{1, -4});
    }

    // Note that in mlpack the features are the rows, while the columns are the
    // samples -> That is why we have a transpose here
    LinearRegression lr(data.st(), responses);
    arma::vec parameters = lr.Parameters();

    parameters.print("Regression Parameters: ");
    arma::vec{0, 1, -4}.print("Correct parameters:");
}
