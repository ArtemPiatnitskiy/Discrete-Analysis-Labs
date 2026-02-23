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
    // Дефолтный конструктор
    Car() = default;

    Car(const std::string& number, const std::string& id) : number(number), id(id) {}
    std::string number;
    std::string id;
};


uint32_t normalize_number(std::string& number) {
    uint32_t result = 0;
    for (int i = 0; i < 8; ++i) {
        if (number[i] >= '0' && number[i] <= '9') {
            result = result * 256 + (number[i] - '0');
        }
        if (number[i] >= 'A' && number[i] <= 'Z') {
            result = result * 256 + (number[i] - 'A' + 10);
        }
    }
    return result;
} 


void counting_sort(Vector<Car>& cars, int shift) {
    int k = 256;

    Vector<int> counter(k, 0);

    for (const auto& car : cars) {
         unsigned char c = ((unsigned int)shift < car.number.size()) ? static_cast<unsigned char>(car.number[shift]) : 0;
        ++counter[c];
    }

    for (int i = 1; i < k; ++i) {
        counter[i] += counter[i - 1];
    }

    Vector<Car> res(cars.size());
    for (int i = cars.size() - 1; i >= 0; --i) {
        --counter[cars[i].number[shift]];
        res[counter[cars[i].number[shift]]] = cars[i];
    }
    cars.swap(res);
}

void radix_sort(Vector<Car>& cars) {
    for (int shift = 7; shift >=0; --shift) {
        counting_sort(cars, shift);
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
        // size_t delimiterPos = 8;
        if (delimiterPos == std::string::npos) continue;
        cars.pushBack(Car(inputLine.substr(0, delimiterPos), inputLine.substr(delimiterPos + 1)));
    }

    radix_sort(cars);

    for (const auto& car : cars) {
        std::cout << car.number << '\t' << car.id << '\n';
    }

    return 0;
}