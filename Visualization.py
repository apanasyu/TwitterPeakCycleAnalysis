def vizUsingFollowerSnapshots(userName, iterations, size, followersDir, outputDir, port): 
    from EvolvingPopularity import getHoursAccordingToFollowerOrder
    hoursInOrder, datesInOrder = getHoursAccordingToFollowerOrder(userName, followersDir, port)
    timeHistogramValues = hoursInOrder
    import numpy as np
    import pandas as pd
    pandasDict = {}
    hours = []
    minHour = 0
    maxHour = 24
    for i in range(minHour, maxHour, 1):
        pandasDict[str(i)] = []
        hours.append(str(i))
    pandasDict["key"] = []

    for i in range(0,iterations,1):
        start = i*size
        end = start+size
        #print "main2", start, end
        timeDist = getTimeDist(timeHistogramValues[start:end])
        #print timeDist
        pandasDict["key"].append(start)
        for hour in hours:
            if hour in timeDist:
                pandasDict[hour].append(timeDist[hour])
            elif int(hour) in timeDist:
                pandasDict[hour].append(timeDist[int(hour)])
            else:
                pandasDict[hour].append(0)
                
    idToTimeDF = pd.DataFrame.from_dict(pandasDict)
    idToTimeDF = idToTimeDF[hours+['key']]
    idToTimeDF.to_csv(outputDir+str(userName)+"_24distPlot_"+str(iterations)+".csv", index=True)
    normalizedTimeDistDF = idToTimeDF[hours].div(idToTimeDF[hours].sum(axis=1), axis=0)
    normalizedTimeDistDF = normalizedTimeDistDF.dropna()
    normalizedTimeDistDF.to_csv(outputDir+str(userName)+"_Norm24distPlot_"+str(iterations)+".csv", index=True)
    if len(normalizedTimeDistDF) > 0:
        #print(normalizedTimeDistDF.head(2))
        snapShots = normalizedTimeDistDF.values.tolist()
        x = []
        yFunct = []
        for i in range(0, len(snapShots), 1):
            x.append(float(i))
            a = snapShots[i].index(np.max(snapShots[i]))
            yFunct.append(float(a))
        
        from EvolvingPopularity import cos_sim
        startHour = yFunct[0]
        print("startHour " + str(startHour))
        cosineSim = []
        cosineDist = []
        for y in yFunct:
            cosSimiliarity = cos_sim(startHour, y)
            cosDistance = 1-cosSimiliarity
            cosineSim.append(cosSimiliarity)
            cosineDist.append(cosDistance)
            
        import matplotlib.pyplot as plt
        plt.scatter(x,cosineSim)
        plt.plot(x,cosineSim)
        plt.xlabel("Time Distribution Count")
        plt.ylabel("Cosine Similarity")
        plt.title("Cosine Similarity between Initial Peak Hour\n vs. peak hours observed in 40 Time Distributions for @CNN", fontsize=12)
        
        pathToSaveTo = outputDir+"CosineSimilarity"+str(userName)+".png"
        plt.savefig(pathToSaveTo, bbox_inches='tight', dpi = 600)
        plt.close()
        print("written fig to " + pathToSaveTo)
        
        CosineDistanceViz = False
        if CosineDistanceViz:
            import matplotlib.pyplot as plt
            plt.plot(x,cosineDist)
            plt.scatter(x,cosineDist)
            plt.xlabel("Time Distribution Count")
            plt.ylabel("Cosine Similarity")
            plt.title("Cosine Similarity between Initial Peak Hour\n vs. peak hours observed in 40 Time Distributions for @CNN", fontsize=12)
            
            pathToSaveTo = outputDir+"CosineDistance"+str(userName)+".png"
            plt.savefig(pathToSaveTo, bbox_inches='tight', dpi = 600)
            plt.close()
            print("written fig to " + pathToSaveTo)
        
        if True:
            import matplotlib.pyplot as plt
            barsAllT = []
            labels = []
            for i in range(0, len(snapShots), 1):
                barsAllT.append(snapShots[i])
                labels.append(str(i))
            
            barsAll = []
            multiplier = 1
            count = 0
            for l in barsAllT:
                l = [x * multiplier for x in l]
                barsAll.append(l)
                count += 1
            # The position of the bars on the x-axis
            bars1 = barsAll[0]
            N = len(bars1)
            r = np.arange(N)
             
            # Names of group and bar width
            names = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23']
            import matplotlib
            #cmap = matplotlib.cm.get_cmap('winter')
            cmap = matplotlib.cm.get_cmap('Greys')
            barWidth = 1
            i = 0
            #plt.bar(r, bars1, edgecolor='white', color=cmap(float(i)/float(len(barsAll))), width=barWidth, label=labels[0])    
            #plt.plot(range(0,24,1), bars1, color=cmap(float(i)/float(len(barsAll))))
            plt.plot(range(0,24,1), np.array(barsAll[0]), linewidth=0.5, alpha=0.5, color="black")
            plt.scatter(range(0,24,1), np.array(barsAll[0]), color="black", alpha=0.5, s=1)
            xToConnect = []
            yToConnect = []
            plt.scatter(snapShots[i].index(np.max(snapShots[i])), np.max(snapShots[i])*multiplier, color="red", alpha=1, s=5)
            #plt.scatter(snapShots[i].index(np.min(snapShots[i])), np.min(snapShots[i]), color="blue", alpha=0.5)
            xToConnect.append(snapShots[i].index(np.max(snapShots[i])))
            yToConnect.append(np.max(snapShots[i]))
            bottomBars = [0]*N
            bottomBarValue = np.max(barsAll[0])+((0.4-np.max(barsAll[0]))*multiplier)
            for i in range(1, len(barsAll), 1):
                bottomBars = [bottomBarValue]*N
                plt.plot(range(0,24,1), np.array(barsAll[i])+bottomBarValue, linewidth=0.5, alpha=0.5, color="black")
                plt.scatter(range(0,24,1), np.array(barsAll[i])+bottomBarValue, color="black", alpha=0.5, s=1)
                plt.scatter(snapShots[i].index(np.max(snapShots[i])), np.max(snapShots[i])*multiplier+bottomBarValue, color="red", alpha=1, s=5)

                xToConnect.append(snapShots[i].index(np.max(snapShots[i])))
                yToConnect.append(np.max(snapShots[i])+bottomBarValue)
                bottomBarValue += np.max(barsAll[i])+((0.4-np.max(barsAll[i]))*multiplier)
            plt.xticks(r, names)
            plt.xlabel("Hours", fontsize=12)
            plt.title(str(iterations) + " Time Distributions\nFormed over different portions of @" + str(userName).upper() + "'s followers", fontsize=12)
            frame1 = plt.gca()
            #frame1.axes.xaxis.set_ticklabels([])
            frame1.axes.yaxis.set_ticklabels([])
            frame1.axes.get_yaxis().set_visible(False)
            
            pathToSaveTo = outputDir+"StackedDist"+str(userName)+".png"
            plt.savefig(pathToSaveTo, bbox_inches='tight', dpi = 1200)
            print("written fig to " + pathToSaveTo)
            
def getTimeDist(timeValues):
    timeDist = {}
    for timeValue in timeValues:
        if not timeValue in timeDist:
            timeDist[timeValue] = 1
        else:
            timeDist[timeValue] += 1

    return timeDist
