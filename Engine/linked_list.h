#pragma once
#include <string>

struct MovementNode {
    int row;            
    int col;            
    int step;           
    MovementNode* next;

    MovementNode(int r, int c, int step);
};

class MovementList {
public:
    MovementList();
    ~MovementList();

    void append(int row, int col, int step); 
    void clear();                            
    bool contains(int row, int col) const;   
    int  getSize() const;
    MovementNode* getHead() const;

    std::string toJson() const;              
    void print() const;                      

private:
    MovementNode* head;
    MovementNode* tail;
    int size;
};