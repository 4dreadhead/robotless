package main

import (
    "fmt"
    "io/ioutil"
    "net/http"
    "os"
    "runtime"
)

func main() {
    version := runtime.Version()

    url := "https://tls.browserleaks.com/json"

    response, err := http.Get(url)
    if err != nil {
        fmt.Println("Ошибка при выполнении запроса:", err)
        return
    }
    defer response.Body.Close()

    responseBody, err := ioutil.ReadAll(response.Body)
    if err != nil {
        fmt.Println("Ошибка при чтении ответа:", err)
        return
    }

    fileName := fmt.Sprintf("results/go_nethttp-%s.json", version)

    file, err := os.Create(fileName)
    if err != nil {
        fmt.Println("Ошибка при создании файла:", err)
        return
    }
    defer file.Close()

    _, err = file.Write(responseBody)
    if err != nil {
        fmt.Println("Ошибка при записи данных в файл:", err)
        return
    }
}