def performPeakAnalysis(userName, followersDir, outputDir, port, step):
    from EvolvingPopularity import getHoursAccordingToFollowerOrder
    hoursInOrder, datesInOrder = getHoursAccordingToFollowerOrder(userName, followersDir, port)
    
    L1 = hoursInOrder
    iterations = int(len(L1)/step)

    import numpy as np
    x1 = []
    x2 = []
    peaks = []
    count = 0
    for i1 in range(0, iterations, 1):
        hoursV = L1[i1*step:i1*step+step]
        
        hoursH = [0]*24
        for h in hoursV: hoursH[h] += 1
        
        normH = [float(i2)/np.sum(hoursH) for i2 in hoursH]
        peaks.append(normH.index(np.max(normH)))
        x1.append(i1)
        x2.append(count)
        count += 1
    
    from EvolvingPopularity import cos_sim
    cosineSim = [cos_sim(peaks[0], h) for h in peaks]
    
    rows = [["x1", "x2", "peak", "cosineSim"]]
    for i in range(0, len(x1), 1):
        rows.append([x1[i], x2[i], peaks[i], cosineSim[i]])
    
    outpath = outputDir+userName+"_"+str(step)+".csv"
    from EvolvingPopularity import writeRowsToCSV
    writeRowsToCSV(rows, outpath)
    print("written results to " + outpath)

def preprocessUsernames(userNames, followersDir, outputDir, port, step):
    import os
    import pandas as pd
    import numpy as np
    peakOutputPaths = []
    iterations = []
    for userName in userNames:
        peakOutputPath = outputDir+userName+"_"+str(step)+".csv"
        if not os.path.exists(peakOutputPath):
            performPeakAnalysis(userName, followersDir, outputDir, port, step)
        df=pd.read_csv(peakOutputPath, encoding='utf-8')
        iterations.append(len(list(df['x2'])))
        peakOutputPaths.append(peakOutputPath)
    
    maxIterations = np.min(iterations) #want to generate visualization where data is present for all influencers (i.e. if one influence has 100K followers and other has 5K followers the first 5K followers analyzed in each
    
    return peakOutputPaths, maxIterations

def cosineSimilarityBetweenPeaks(userNames, followersDir, outputDir, port, step):
    if len(userNames) != 2:
        print("error visualization designed to compare two users")
        import sys
        sys.exit()
        
    inpaths, maxIterations = preprocessUsernames(userNames, followersDir, outputDir, port, step)
    labels = userNames
    
    count = 0
    for inpath in inpaths:
        import pandas as pd
        df=pd.read_csv(inpath, encoding='utf-8')
        df = df.loc[(df['x2'] <= maxIterations)]
        df["x2"] = df["x2"]*step
        x = df["x2"]
        y = df["cosineSim"]
        
        import matplotlib.pyplot as plt
        plt.rcParams["figure.figsize"] = (12,4)
        if count == 0:
            plt.scatter(x,y, label=labels[count], alpha=0.5, color="blue")
            plt.plot(x,y, alpha=1, label='_nolegend_')
        else:
            plt.scatter(x,y, label=labels[count], alpha=0.5, color="orange")
            plt.plot(x,y, alpha=1, label='_nolegend_')
        influencer = labels[count]
        
        if False:
            outpath = outputDir1+influencer+"CosineSim.csv"
            import pandas as pd
            df=pd.read_csv(outpath, encoding='utf-8')
            dayToFollowerChange = dict(zip(list(df["day"]), list(df["turnRate"])))
            
            followerCountMax = iterations*step
            followerCount = 0
            for day in dayToFollowerChange:
                lineX = followerCount + dayToFollowerChange[day]
                if lineX < followerCountMax:
                    if count == 0:
                        plt.axvline(lineX,0,0.03, linewidth=5, color="black")
                    else:
                        plt.axvline(lineX,1,0.97, linewidth=3, color="black")
                else:
                    break
                followerCount += dayToFollowerChange[day]
        count += 1
        
    plt.xlabel("Follower Count", fontSize=12)
    plt.ylabel("Cosine Similarity", fontSize=12)
    plt.title("Peak of each time distribution forms a pattern.\nPeriod of pattern related to number of followers gained on a daily basis.", fontSize=12)
    
    pathToSaveTo = outputDir+"CosineSimilarityBetweenPeaks.png"
    plt.legend(ncol=1, fancybox=True)
    plt.savefig(pathToSaveTo, bbox_inches='tight', dpi = 1200)
    print("written fig to " + pathToSaveTo)

def peakVisualization(userNames, followersDir, outputDir, port, step):
    if len(userNames) != 2:
        print("error visualization designed to compare two users")
        import sys
        sys.exit()
        
    inpaths, maxIterations = preprocessUsernames(userNames, followersDir, outputDir, port, step)
    labels = userNames
    
    import matplotlib.pyplot as plt
    plt.rcParams["figure.figsize"] = (12,4)
    count = 0
    for inpath in inpaths:
        import pandas as pd
        df=pd.read_csv(inpath, encoding='utf-8')
        print(df.columns)
        df = df.loc[(df['x2'] <= maxIterations)]
        df["x2"] = df["x2"]*step
        x = df["x2"]
        y = df["peak"]
        if count == 0:
            plt.scatter(x,y,color='blue',alpha=1, s=1, label=labels[count])
        else:
            plt.scatter(x,y-0.25,color='red',alpha=1, s=1, label=labels[count])
        count += 1
    
    plt.xlabel("Follower Count", fontsize=12)
    plt.ylabel("Hour at which Distribution Peaks", fontsize=12)
    plt.title("Peaks of time distributions for followers of " + str(labels[0]) + " (blue) vs. " + str(labels[1]) + " (red)", fontsize=12)
    
    plt.legend(ncol=1, fancybox=True)
            
    pathToSaveTo = outputDir+"PeakAnalysis.png"
    plt.savefig(pathToSaveTo, bbox_inches='tight', dpi = 1200)
    plt.close()
    print("written fig to " + pathToSaveTo)