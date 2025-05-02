import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

class ContentBasedRecommender:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Load or initialize item data
        self.items = self._load_data("items.csv",
            columns=["item_id", "title", "genres", "description"],
            default_data=[
                (101, "The Shawshank Redemption", "Drama", "Two imprisoned men bond over several years..."),
                (102, "The Godfather", "Crime,Drama", "The aging patriarch of an organized crime dynasty..."),
                (103, "The Dark Knight", "Action,Crime,Drama", "When the menace known as the Joker emerges..."),
                (104, "Pulp Fiction", "Crime,Drama", "The lives of two mob hitmen, a boxer, a gangster..."),
                (105, "Fight Club", "Drama", "An insomniac office worker and a devil-may-care soapmaker...")
            ])
        
        # Prepare content features
        self._prepare_features()
    
    def _load_data(self, filename: str, columns: list, default_data: list) -> pd.DataFrame:
        """Load data from file or use default data if file doesn't exist"""
        path = os.path.join(self.data_dir, filename)
        if os.path.exists(path):
            return pd.read_csv(path)
        else:
            df = pd.DataFrame(default_data, columns=columns)
            df.to_csv(path, index=False)
            return df
    
    def _prepare_features(self):
        """Prepare TF-IDF features from item content"""
        # Combine genres and description for better recommendations
        self.items["content"] = self.items["genres"] + " " + self.items["description"]
        
        # Create TF-IDF vectorizer
        self.tfidf = TfidfVectorizer(stop_words="english", max_features=500)
        self.content_features = self.tfidf.fit_transform(self.items["content"])
        
        # Calculate item similarity matrix
        self.item_similarity = cosine_similarity(self.content_features)
    
    def recommend_similar_items(self, item_id: int, n: int = 5) -> list:
        """Recommend similar items based on content"""
        if item_id not in self.items["item_id"].values:
            return []
            
        item_idx = self.items[self.items["item_id"] == item_id].index[0]
        similar_indices = self.item_similarity[item_idx].argsort()[::-1][1:n+1]
        
        recommendations = []
        for idx in similar_indices:
            similar_item = self.items.iloc[idx]
            similarity_score = self.item_similarity[item_idx][idx]
            recommendations.append({
                "item_id": similar_item["item_id"],
                "title": similar_item["title"],
                "similarity": float(similarity_score)  # Convert numpy float to Python float
            })
        
        return recommendations
    
    def add_item(self, item_id: int, title: str, genres: str, description: str):
        """Add new item to the system"""
        new_item = pd.DataFrame([[item_id, title, genres, description]], 
                              columns=["item_id", "title", "genres", "description"])
        self.items = pd.concat([self.items, new_item], ignore_index=True)
        self._prepare_features()  # Recalculate features
        self._save_data()
    
    def _save_data(self):
        """Save current data to file"""
        self.items.to_csv(os.path.join(self.data_dir, "items.csv"), index=False)
    
    def get_item_title(self, item_id: int) -> str:
        """Get item title by ID"""
        item = self.items[self.items["item_id"] == item_id]
        return item["title"].values[0] if not item.empty else "Unknown"

def main():
    recommender = ContentBasedRecommender()
    
    print("Item Catalog:")
    print(recommender.items[["item_id", "title"]].to_string(index=False))
    
    while True:
        print("\nOptions:")
        print("1. Get similar items")
        print("2. Add new item")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == "1":
            item_id = int(input("Enter item ID: "))
            recs = recommender.recommend_similar_items(item_id)
            print(f"\nItems similar to {recommender.get_item_title(item_id)}:")
            for rec in recs:
                print(f"- {rec['title']} (ID: {rec['item_id']}, similarity: {rec['similarity']:.2f})")
                
        elif choice == "2":
            item_id = int(input("Enter new item ID: "))
            title = input("Enter title: ")
            genres = input("Enter genres (comma separated): ")
            description = input("Enter description: ")
            recommender.add_item(item_id, title, genres, description)
            print("Item added successfully!")
            
        elif choice == "3":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()