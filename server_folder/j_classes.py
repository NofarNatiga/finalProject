from typing import List, Union
from dataclasses import dataclass
import os


@dataclass
class Category:
    name: str
    associated_works: list['Work']
    description: str

    @classmethod
    def load(cls, data: dict[str, Union[str, list['Work']]]) -> 'Category':
        associated_works_data = data.get("associated_works", [])
        print(f"Loading associated works: {associated_works_data}")  # Debugging
        return cls(name=data["name"], associated_works=[Work.load(work_data) for work_data in associated_works_data],
                   description=data["description"])

    def dump(self) -> dict[str, Union[str, list['Work']]]:
        return {"name": self.name, "associated_works": [work.dump() for work in self.associated_works],
                "description": self.description}

    def add_work(self, work: 'Work'):
        self.associated_works.append(work)

    def remove_work(self, work: 'Work'):
        self.associated_works.remove(work)


@dataclass
class Work:
    title: str
    category_names: list[str]
    description: str
    rating: int
    image_path: str
    date: str
    public: bool

    @classmethod
    def load(cls, data: dict[str, (str, List[str], int, bool)]) -> 'Work':
        return cls(
            title=data["title"],
            category_names=data["category_names"],
            description=data["description"],
            rating=data["rating"],
            image_path=data["image_path"],
            date=data["date"],
            public=data["public"]
        )

    def dump(self) -> dict[str, (str, List[str], int)]:
        return {
            "title": self.title,
            "category_names": self.category_names,
            "description": self.description,
            "rating": self.rating,
            "image_path": self.image_path,
            "date": self.date,
            "public": self.public
        }

@dataclass
class User_Data:
    name: str
    all_works: list[Work]
    all_categories: list[Category]

    @classmethod
    def load(cls, data: dict) -> 'User_Data':
        all_works = [Work.load(work_data) for work_data in data["all_works"]]
        all_categories = [Category.load(cat_data) for cat_data in data["all_categories"]]
        return cls(name=data["name"], all_works=all_works, all_categories=all_categories)

    def dump(self) -> dict:
        return {
            "name": self.name,
            "all_works": [work.dump() for work in self.all_works],
            "all_categories": [cat.dump() for cat in self.all_categories],
        }

    def add_work(self, work: Work):
        existing_titles = [w.title for w in self.all_works]
        if work.title in existing_titles:
            work.title = self.new_work_title(work.title)

        self.all_works.append(work)

        # Add the work to the appropriate categories or create new categories if needed
        for category_name in work.category_names:
            flag = False
            for category in self.all_categories:
                if category.name == category_name:
                    category.add_work(work)
                    flag = True
                    print("flag = True")
                    break
            if flag is False:
                print("here flag is false")
                new_category = Category(name=category_name, associated_works=[work, ], description="")
                print(new_category.associated_works)
                self.add_category(new_category)

    def new_work_title(self, title: str) -> str:
        suffix = 1
        while f"{title}{suffix}" in [w.title for w in self.all_works]:  # making a unique title
            suffix += 1
        return f"{title}{suffix}"

    def new_category_name(self, name: str) -> str:
        suffix = 1
        while f"{name}{suffix}" in [c.name for c in self.all_categories]:  # making a unique title
            suffix += 1
        return f"{name}{suffix}"

    def add_group(self, group: Group):
        pass

    def add_category(self, category: Category):
        existing_titles = [c.name for c in self.all_categories]
        if category.name in existing_titles:
            category.name = self.new_category_name(category.name)
        self.all_categories.append(category)

    def remove_work(self, work_title: str):
        response = {"response": "work not found"}
        for work in self.all_works:
            if work.title == work_title:
                response = {"response": "work deleted successfully", "path": work.image_path}
                os.remove(work.image_path)  # deleting from server
                self.all_works.remove(work)
                for category in self.all_categories:
                    if category.name in work.category_names:
                        category.remove_work(work)
        return response

    def remove_category(self, category_name: str):
        # Remove category from list of categories
        for c in self.all_categories:
            if c.name == category_name:
                self.all_categories.remove(c)
                # Remove category name from associated works
                for work in self.all_works:
                    if category_name in work.category_names:
                        work.category_names.remove(category_name)
                return {"response": "category deleted successfully"}
        return {"response": "category not found"}

    def update_work_details(self, work_title: str, new_details: dict):
        for work in self.all_works:
            if work.title == work_title:
                old_category_names = work.category_names.copy()
                for key, value in new_details.items():
                    setattr(work, key, value)
                for new_category in (set(work.category_names) - set(old_category_names)):
                    for category in self.all_categories:
                        if category.name == new_category:
                            category.add_work(work)
                            break

                # Remove work from categories it's no longer associated with
                for old_category_name in (set(old_category_names) - set(work.category_names)):
                    for category in self.all_categories:
                        if category.name == old_category_name:
                            if work in category.associated_works:
                                category.remove_work(work)
                                break
                return {"response": "work updated successfully"}
            else:
                return {"response": "no such title"}

        print(f"Work with title '{work_title}' not found.")

    def update_category_details(self, category_name: str, category_details: dict):
        for category in self.all_categories:
            if category.name == category_name:
                old_category_name = category_name
                for key, value in category_details.items():
                    setattr(category, key, value)
                if old_category_name != category.name:
                    for work in category.associated_works:
                        work.category_names = [category.name if name == old_category_name else name for name in
                                               work.category_names]
                return {"response": "category updated successfully"}

        return {"response": "category not found"}
