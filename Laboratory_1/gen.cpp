#include <iostream>
#include <cstdlib>
#include <ctime>
#include <string>

int main(int argc, char* argv[]) {
    size_t n = (argc > 1) ? std::atoi(argv[1]) : 100000;
    size_t valueLen = (argc > 2) ? std::atoi(argv[2]) : 64;

    std::srand(std::time(nullptr));

    for (size_t i = 0; i < n; ++i) {
        // Буква A-Z
        char l1 = 'A' + std::rand() % 26;
        // Три цифры 0-9
        char d1 = '0' + std::rand() % 10;
        char d2 = '0' + std::rand() % 10;
        char d3 = '0' + std::rand() % 10;
        // Две буквы A-Z
        char l2 = 'A' + std::rand() % 26;
        char l3 = 'A' + std::rand() % 26;

        std::cout << l1 << ' ' << d1 << d2 << d3 << ' ' << l2 << l3 << '\t';

        // Случайное значение фиксированной длины
        for (size_t j = 0; j < valueLen; ++j) {
            std::cout << (char)('a' + std::rand() % 26);
        }
        std::cout << '\n';
    }
    return 0;
}
