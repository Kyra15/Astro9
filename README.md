# Astro9

Initial plan:
We plan to use lightcurve data from the Fermi Light Curve Repository and MAST library for analysis. We can filter and load this data using api requests and pandas, and from that we can figure out features such as planet radius, orbital period, and orbital radius. We’ll process and manipulate the data using the lightkurve python package. Next, we’ll filter out all the planets that don’t meet our requirements for radius, and then we’ll calculate the habitable zone for that planet by first finding the luminosity of the star and using the formulas from the homework for inner and outer radii. From the planet’s orbital radius and this estimated zone, we can determine whether or not the planet can sustain water, and, theoretically, life. Additionally, we’ll try to create a pipeline for this system in order to automate it and allow for user input of attributes like radius, orbital period, etc. and determine habitability based off of that.

Process:
- Import csv for test data (light curve, host star data)
- Use lightcurve to find radius, orbital period, and orbital radius
- Check if radii is within range (0.5 - 1.5 Re)
- Calculate HZ from host star data
- Check if within zone
- Return if potentially habitable
