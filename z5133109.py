import ast
import json
import matplotlib.pyplot as plt
import pandas as pd
import sys
import os

studentid = os.path.basename(sys.modules[__name__].__file__)


#################################################
# Your personal methods can be here ...
def q5_function(revenue,budget):
	return (revenue-budget)/budget


#################################################


def log(question, output_df, other):
    print("--------------- {}----------------".format(question))
    if other is not None:
        print(question, other)
    if output_df is not None:
        print(output_df.head(5).to_string())


def question_1(movies, credits):
    """
    :param movies: the path for the movie.csv file
    :param credits: the path for the credits.csv file
    :return: df1
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    # Your code goes here ...
    df_movies=pd.read_csv(movies)
    df_credits=pd.read_csv(credits)
    df1=pd.merge(df_movies,df_credits,on='id')

    #################################################

    log("QUESTION 1", output_df=df1, other=df1.shape)
    return df1


def question_2(df1):
    """
    :param df1: the dataframe created in question 1
    :return: df2
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    # Your code goes here ...
    df2=pd.DataFrame(df1,columns=['id', 'title', 'popularity', 'cast', 'crew', 'budget', 'genres', 'original_language', 'production_companies', 'production_countries', 'release_date', 'revenue', 'runtime', 'spoken_languages', 'vote_average', 'vote_count'])
    #################################################

    log("QUESTION 2", output_df=df2, other=(len(df2.columns), sorted(df2.columns)))
    return df2


def question_3(df2):
    """
    :param df2: the dataframe created in question 2
    :return: df3
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    # Your code goes here ...
    df3=df2.set_index('id')

    #################################################

    log("QUESTION 3", output_df=df3, other=df3.index.name)
    return df3


def question_4(df3):
    """
    :param df3: the dataframe created in question 3
    :return: df4
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    # Your code goes here ...
    df4=df3.drop(df3[df3.budget==0].index)
    #################################################

    log("QUESTION 4", output_df=df4, other=(df4['budget'].min(), df4['budget'].max(), df4['budget'].mean()))
    return df4


def question_5(df4):
    """
    :param df4: the dataframe created in question 4
    :return: df5
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    # Your code goes here ...
    df5=df4.copy()
    df5['success_impact']=q5_function(df5['revenue'],df5['budget'])
    #################################################

    log("QUESTION 5", output_df=df5,
        other=(df5['success_impact'].min(), df5['success_impact'].max(), df5['success_impact'].mean()))
    return df5


def question_6(df5):
    """
    :param df5: the dataframe created in question 5
    :return: df6
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    # Your code goes here ...
    df6=df5.copy()
    df6['popularity']=((df6.popularity-df6.popularity.min())/(df6.popularity.max()-df6.popularity.min()))*100
    #################################################

    log("QUESTION 6", output_df=df6, other=(df6['popularity'].min(), df6['popularity'].max(), df6['popularity'].mean()))
    return df6


def question_7(df6):
    """
    :param df6: the dataframe created in question 6
    :return: df7
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    # Your code goes here ...
    df7=df6.copy()
    df7['popularity']=df7['popularity'].astype('int16')
   
    #################################################

    log("QUESTION 7", output_df=df7, other=df7['popularity'].dtype)
    return df7


def question_8(df7):
    """
    :param df7: the dataframe created in question 7
    :return: df8
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    # Your code goes here ...
    df8=df7.copy()
    df8['cast']=[ast.literal_eval(x) for x in df8['cast']]
    total=[]
    for i in df8['cast']:
        temp=[]
        for j in i:
            temp.append(j['character'])
        total.append(sorted(temp))
    tt=[]
    for i in total:
        tt.append(','.join(i))
    df8['cast']=tt
    #################################################

    log("QUESTION 8", output_df=df8, other=df8["cast"].head(10).values)
    return df8


def question_9(df8):
    """
    :param df9: the dataframe created in question 8
    :return: movies
            Data Type: List of strings (movie titles)
            Please read the assignment specs to know how to create the output
    """

    #################################################
    # Your code goes here ...
    df9=df8.copy()
    times=[]
    for x in df9['cast']:
        times.append(len(x.split(',')))
    df9['times']=times
    df9=df9.sort_values(by='times',ascending=0)
    movies=[]
    flag=0
    for i in df9['title']:
        if flag<10:
            movies.append(i)
        else:
            break
        flag+=1
    #################################################

    log("QUESTION 9", output_df=None, other=movies)
    return movies


def question_10(df8):
    """
    :param df8: the dataframe created in question 8
    :return: df10
            Data Type: Dataframe
            Please read the assignment specs to know how to create the output dataframe
    """

    #################################################
    # Your code goes here ...
    df10=df8.copy()
    df10['release_date']=pd.to_datetime(df10.release_date)
    df10=df10.sort_values(by='release_date',ascending=False)
    #################################################

    log("QUESTION 10", output_df=df10, other=df10["release_date"].head(5).to_string().replace("\n", " "))
    return df10


def question_11(df10):
    """
    :param df10: the dataframe created in question 10
    :return: nothing, but saves the figure on the disk
    """

    #################################################
    # Your code goes here ...
    df11=df10.copy()
    df11['genres']=[ast.literal_eval(x) for x in df11['genres']]
    lt=[]
    for i in df11['genres']:
        for j in i:
            lt.append(j['name'])
    re=pd.value_counts(lt)
    plt.pie(re,labels=re.index,autopct='%1.1f%%')
    plt.title('Geners')
    #################################################

    plt.savefig("{}-Q11.png".format(studentid))
    


def question_12(df10):
    """
    :param df10: the dataframe created in question 10
    :return: nothing, but saves the figure on the disk
    """

    #################################################
    # Your code goes here ...
    plt.clf()
    df12=df10.copy()
    df12['production_countries']=[ast.literal_eval(x) for x in df12['production_countries']]
    c_list=[]
    for u in df12['production_countries']:
        for x in u:
            c_list.append(x['name'])
    rea=pd.value_counts(c_list)
    rea=rea.sort_index()
    rea.plot.bar()
    plt.title('Production Country')
    #################################################

    plt.savefig("{}-Q12.png".format(studentid))


def question_13(df10):
    """
    :param df10: the dataframe created in question 10
    :return: nothing, but saves the figure on the disk
    """

    #################################################
    # Your code goes here ...
    plt.clf()
    df13=df10.copy()

    fr_df=df13.query('original_language=="fr"')
    en_df=df13.query('original_language=="en"')
    de_df=df13.query('original_language=="de"')
    ja_df=df13.query('original_language=="ja"')
    it_df=df13.query('original_language=="it"')
    nl_df=df13.query('original_language=="nl"')
    pt_df=df13.query('original_language=="pt"')
    da_df=df13.query('original_language=="da"')
    es_df=df13.query('original_language=="es"')
    ko_df=df13.query('original_language=="ko"')
    zh_df=df13.query('original_language=="zh"')
    sv_df=df13.query('original_language=="sv"')
    af_df=df13.query('original_language=="af"')
    no_df=df13.query('original_language=="no"')
    fi_df=df13.query('original_language=="fi"')

    x='vote_average'
    y='success_impact'
    ax = fr_df.plot.scatter(x=x, y=y, label='fr',color='lightcoral')
    ax = en_df.plot.scatter(x=x, y=y, label='en',color='red',ax=ax)
    ax = de_df.plot.scatter(x=x, y=y, label='de',color='sandybrown',ax=ax)
    ax = ja_df.plot.scatter(x=x, y=y, label='ja',color='orange',ax=ax)
    ax = it_df.plot.scatter(x=x, y=y, label='it',color='gold',ax=ax)
    ax = nl_df.plot.scatter(x=x, y=y, label='nl',color='yellow',ax=ax)
    ax = pt_df.plot.scatter(x=x, y=y, label='pt',color='palegreen',ax=ax)
    ax = da_df.plot.scatter(x=x, y=y, label='da',color='green',ax=ax)
    ax = es_df.plot.scatter(x=x, y=y, label='es',color='lightseagreen',ax=ax)
    ax = ko_df.plot.scatter(x=x, y=y, label='ko',color='aqua',ax=ax)
    ax = zh_df.plot.scatter(x=x, y=y, label='zh',color='deepskyblue',ax=ax)
    ax = sv_df.plot.scatter(x=x, y=y, label='sv',color='blue',ax=ax)
    ax = af_df.plot.scatter(x=x, y=y, label='af',color='darkviolet',ax=ax)
    ax = no_df.plot.scatter(x=x, y=y, label='no',color='purple',ax=ax)
    ax = fi_df.plot.scatter(x=x, y=y, label='fi',color='pink',ax=ax)
    plt.title('vote_average vs. impact_success')
    #################################################

    plt.savefig("{}-Q13.png".format(studentid))


if __name__ == "__main__":
    df1 = question_1("movies.csv", "credits.csv")
    df2 = question_2(df1)
    df3 = question_3(df2)
    df4 = question_4(df3)
    df5 = question_5(df4)
    df6 = question_6(df5)
    df7 = question_7(df6)
    df8 = question_8(df7)
    movies = question_9(df8)
    df10 = question_10(df8)
    question_11(df10)
    question_12(df10)
    question_13(df10)






