#include <iostream>
// #include <vector>
#include <cstddef>
#include <string>
#include <utility>
#include <cstdint>

template<typename T>

class Vector {
    private:
        size_t size_ = 0;
        T* data = nullptr;
        size_t capacity_ = 0;

        void reallocate(size_t newCapacity) {
            T* newData = new T[newCapacity];
            for (size_t i = 0; i < size_; ++i) {
                newData[i] = std::move(data[i]);
            }
            delete[] data;
            data = newData;
            capacity_ = newCapacity;
        }

    public:
        Vector<T>() : size_(0), data(nullptr), capacity_(0) {}

        Vector<T>(size_t size) : size_(size), data(new T[size]), capacity_(size) {}

        Vector<T>(size_t size, const T& value) : size_(size), data(new T[size]), capacity_(size) {
            for (size_t i = 0; i < size_; ++i) {
                data[i] = value;
            }
        }

        // Конструктор перемещения
        Vector(Vector<T>&& other) noexcept : size_(other.size_), data(other.data), capacity_(other.capacity_) {
            other.size_ = 0;
            other.data = nullptr;
            other.capacity_ = 0;
        }

        ~Vector() {
            delete[] data;
            size_ = 0;
            capacity_ = 0;
        }

        size_t size() const {
            return size_;
        }

        size_t capacity() const {
            return capacity_;
        }

        void clear() {
            size_ = 0;
        }

        void shrinkToFit() {
            if (size_ < capacity_) {
                reallocate(size_);
            }
        }

        void pushBack(const T& value) {
            if (size_ == capacity_) {
                reallocate(capacity_ == 0 ? 1 : capacity_ * 2);
            }
            data[size_] = value;
            size_++;
        }

        void popBack() {
            if (size_ > 0) {
                size_--;
            }
        }

        T& operator[](size_t index) {
            return data[index];
        }

        const T& operator[](size_t index) const {
            return data[index];
        }

        bool empty() const {
            return size_ == 0;
        }

        bool operator==(const Vector<T>& other) const {
            if (size_ != other.size_) {
                return false;
            }
            for (size_t i = 0; i < size_; ++i) {
                if (data[i] != other.data[i]) {
                    return false;
                }
            }
            return true;
        }

        bool operator!=(const Vector<T>& other) const {
            return !(*this == other);
        }

        T* begin() {
            return data;
        }

        T* end() {
            return data + size_;
        }

        const T* begin() const {
            return data;
        }

        const T* end() const {
            return data + size_;
        }

        void swap(Vector<T>& other) {
            std::swap(size_, other.size_);
            std::swap(data, other.data);
            std::swap(capacity_, other.capacity_);
        }
};


struct Car {
    Car() = default;
    Car(uint32_t key, const std::string& id) : key(key), id(id) {}
    uint32_t key = 0;
    std::string id;
};


uint32_t encodeNumber(const std::string& number) {
    uint32_t result = 0;
    result += (number[0] - 'A') << 22;
    result += (number[2] - '0') << 18;
    result += (number[3] - '0') << 14;
    result += (number[4] - '0') << 10;
    result += (number[6] - 'A') << 5;
    result += (number[7] - 'A');
    return result;
}


std::string decodeNumber(uint32_t number) {
    std::string result(8, ' ');
    result[0] = ((number >> 22) & 31) + 'A';
    result[2] = ((number >> 18) & 15) + '0';
    result[3] = ((number >> 14) & 15) + '0';
    result[4] = ((number >> 10) & 15) + '0';
    result[6] = ((number >> 5) & 31) + 'A';
    result[7] = (number & 31) + 'A';
    return std::string(result);
}


void counting_sort(Vector<Car>& cars, Vector<Car>& res, int R, int shift) {
    const int k = 256;
    const uint32_t mask = 255u << (R * shift);

    Vector<int> counter(k, 0);

    for (size_t i = 0; i < cars.size(); ++i) {
        ++counter[(cars[i].key & mask) >> (R * shift)];
    }

    for (int i = 1; i < k; ++i) {
        counter[i] += counter[i - 1];
    }

    for (int i = cars.size() - 1; i >= 0; --i) {
        int pos = --counter[(cars[i].key & mask) >> (R * shift)];
        res[pos] = std::move(cars[i]);
    }
}

void radix_sort(Vector<Car>& cars) {
    Vector<Car> res(cars.size());

    for (int shift = 0; shift < 4; ++shift) {
        counting_sort(cars, res, 8, shift);
        cars.swap(res);
    }
}


int main() {
    std::string inputLine;

    Vector<Car> cars;

    while(std::getline(std::cin, inputLine)) {
        if (inputLine.empty()) {
            continue;
        }
        size_t delimiterPos = inputLine.find('\t');
        if (delimiterPos == std::string::npos) continue;
        cars.pushBack(Car(encodeNumber(inputLine.substr(0, delimiterPos)),
                          inputLine.substr(delimiterPos + 1)));
    }
    cars.shrinkToFit();

    radix_sort(cars);

    for (const auto& car : cars) {
        std::cout << decodeNumber(car.key) << '\t' << car.id << '\n';
    }

    return 0;
}