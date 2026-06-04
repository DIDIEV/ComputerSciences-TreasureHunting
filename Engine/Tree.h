#pragma once
#include <string>

struct TreasureNode {
    int         treasureId;     
    int         value;          
    int         row;            
    int         col;
    std::string name;           
    bool        collected;      

    TreasureNode* left;
    TreasureNode* right;

    TreasureNode(int id, int val, int r, int c, const std::string& name);
};

class TreasureBST {
public:
    TreasureBST();
    ~TreasureBST();

    void insert(int id, int value, int row, int col, const std::string& name);
    bool collect(int id);                        
    TreasureNode* findMaxUncollected() const;    
    TreasureNode* findMinUncollected() const;    
    int  countUncollected() const;
    int  getNodeCount() const;
    int  height() const;

    
    std::string toJson() const;   

    
    void printInOrder() const;

private:
    TreasureNode* root;
    int nodeCount;

    TreasureNode* insertRec(TreasureNode* node, int id, int value,
                             int row, int col, const std::string& name);
    bool collectRec(TreasureNode* node, int id);
    TreasureNode* findMaxUncollectedRec(TreasureNode* node,
                                        TreasureNode* best) const;
    TreasureNode* findMinUncollectedRec(TreasureNode* node,
                                        TreasureNode* best) const;
    int  countUncollectedRec(TreasureNode* node) const;
    int  heightRec(TreasureNode* node) const;
    void inOrderJson(TreasureNode* node, std::string& json, bool& first) const;
    void printInOrderRec(TreasureNode* node) const;
    void destroyTree(TreasureNode* node);
};