package main

import (
    "encoding/json"
    "log"
    "net/http"
)

type User struct {
    ID       int      json:"id"  
    Name     string   json:"name"  
    Email    string   json:"email"  
    Password string   json:"password"  
}

var users []User

func main() {
    http.HandleFunc("/users", getUsers)
    http.HandleFunc("/users/add", addUser)
    http.HandleFunc("/users/delete", deleteUser)

    log.Fatal(http.ListenAndServe(":8080", nil))
}

func getUsers(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(users)
}

func addUser(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    var user User
    err := json.NewDecoder(r.Body).Decode(&user)
    if err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }
    users = append(users, user)
    json.NewEncoder(w).Encode(users)
}

func deleteUser(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    var user User
    err := json.NewDecoder(r.Body).Decode(&user)
    if err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }
    for i, u := range users {
        if u.ID == user.ID {
            users = append(users[:i], users[i+1:]...)
            break
        }
    }
    json.NewEncoder(w).Encode(users)
}

// This code defines a simple REST API with three endpoints:   /users   to get all users,   /users/add   to add a new user, and   /users/delete   to delete a user by ID. The implementation uses the built-in   http   package to handle incoming requests and   json   package to encode and decode JSON data.