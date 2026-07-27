from database import get_companies


companies = get_companies()


print("Total Companies:", len(companies))


print("\nFirst 10 Companies:")
print(companies.head(10))