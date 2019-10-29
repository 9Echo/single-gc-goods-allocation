import pandas as pd


def test_df():
    data = [['Alex', 10], ['Bob', 12], ['Clarke', 13]]
    df = pd.DataFrame(data, columns=['Name', 'Age'], dtype=float)
    print('list list to df:\n', df)

    data = (('Alex', 10), ('Bob', 12), ('Clarke', 13))
    df = pd.DataFrame(list(data), columns=['Name', 'Age'], dtype=float)
    print('tuple list to df:\n', df)

    data = {'Name': ['Tom', 'Jack', 'Steve', 'Ricky'], 'Age': [28, 34, 29, 42]}
    df = pd.DataFrame(data)
    print('list dict to df:\n', df)
    df = pd.DataFrame(data, index=['rank1', 'rank2', 'rank3', 'rank4'])
    print('list dict to df2:\n', df)

    data = [{'a': 1, 'b': 2}, {'a': 5, 'b': 10}]
    df = pd.DataFrame(data)
    print('dict list to df:\n', df)
    data = [{'a': 1, 'b': 2}, {'a': 5, 'b': 10, 'c': 20}, {'a': 10, 'b': 11}, {'a': 20, 'b': 21}]
    df = pd.DataFrame(data, index=['first', 'second', 'third', 'fourth'])
    print('dict list to df2:\n', df)
    print('dict list to df2 -> slice:\n', df[1:4])
    print('dict list to df2 -> value:\n', df.values)
    print('dict list to df2 -> row:\n', df.iloc[1])


if __name__ == "__main__":
    test_df()
