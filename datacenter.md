# Data Center

## E.Datacenter.2.b
Microsoft's Columbia data center at Quincy Washington is a 470,000 sqft. 
facility built in 2007. Located close to the Columbia River, it benefits from the hydro electric energy generated from the river. The location also has other advantages such as low land costs, abundant data fiber and low cost electricity. 

Reference : <https://en.wikipedia.org/wiki/Columbia_Data_Center>

**IT Load** - In Microsoft Ignite presentation, Microsoft Azure CTO Mark Russinovich sampled out Columbia data center and mentioned it has a 
capacity of 64MW. He specified that there are two datacenters consisting four independent 8MW colocations totaling to a 64MW (64000kW) capacity, hence this value is chosen as the IT Load for the data center.

Reference: <https://www.youtube.com/watch?v=D8hMu4jJAwo>

**Cost per kWH** - 
The Grant PUD county rate for large industrial consumers consuming greater than 15MW is $0.03/kwH but according to a portofquincy.org web article, Microsoft is receiving a rate of $0.019 hence this cost is being used. 

Reference:
<http://www.portofquincy.org/category/blog/page/2/>

<https://www.grantpud.org/rates-fees>

**Electricity Cost ($/kW)** - The yearly cost is calculated with power consumption rate of 64MW at the cost of $0.019 assuming that the data center is 100% available in a year.
 
 64000 * 24 * 0.019 * 365 = $10,652,160

**Yearly CO2 Footprint (tons) and	CO2 equivalent in cars** -
Using the Carbon emission calculator the CO2 emission value and C02 equivalent in cars is derived. The average PUE Microsoft's data center is 1.125 is used here and cost is 0.019/kWH is used for this calculation.

CO2 Emission - 62250.72 Tons

CO2 equivalent in cars - 13724

Tool : Schneider electric Carbon Emission Calculation link -
<https://www.schneider-electric.com/en/work/solutions/system/s1/data-center-and-network-systems/trade-off-tools/data-center-carbon-footprint-comparison-calculator/> 

Reference - 
<http://download.microsoft.com/download/8/2/9/8297f7c7-ae81-4e99-b1db-d65a01f7a8ef/microsoft_cloud_infrastructure_datacenter_and_network_fact_sheet.pdf>

## E.Datacenter.4

**Hydro Energy**

* Britannica definition states that "Hydroelectric power, electricity produced from generators driven by turbines that convert the potential energy of falling or fast-flowing water into mechanical energy."
* Hydro energy is one of the oldest sources for generating mechanical and electrical energy. This was used years ago to turn paddle wheels to grind grains. Hydro electricity is largely produced at major rivers or large dams.
* In Hydro power plants, Water conserved in a reservoir gains potential energy just before it flows downhill. As water gets released, the potential energy is converted to kinetic energy. This is used to turn the blades of a turbine in order to generate electricity which is in turn distributed to power plants.
* Hydro power is environment friendly compared to fossil fuels, coal or oil.
* A Hydro power plant can be used a peaking power plant when demand increases. When needed, the water stored in reservoir can be released and energy can be produced quickly.
* Top providers of hydroelectricity include China, United States, Canada, Brazil and India. Of all renewable energy, 71% of renewable electricity is from Hydro energy.

Reference - <https://www.nationalgeographic.org/encyclopedia/hydroelectric-energy>

<https://www.eia.gov/energyexplained/hydropower/>

<https://www.britannica.com/science/hydroelectric-power>

<https://simple.wikipedia.org/wiki/Hydroelectricity>


## E.Datacenter.5

**Germany**

* Germany's major renewable sources are from Wind energy, Solar energy and Biomass.
* In April 2019, Germany's renewable energy accounted for 77% of Germany's net public power supply with the advantage from strong winds and abundant sunshine. On the whole, Wind power provided 40 percent, solar 20 percent, and biomass 10 percent of renewable energy.
* According to wikipedia, The German energy policy is framed within the European Union which has a mandatory energy plan that requires a 20% reduction of CO2 emissions before year 2020 and the consumption of renewable energies to be 20% of total EU consumption.
* Germany has one of largest wind turbine in the world, and its wind farm operates in averages of 10,500MWh a year. Through such efforts, 113.35TWh of electricity in generated in Germany in 2018.
* Germany's renewable energy innovations have opened up an entirely new job sector based on technology development, production, installation and maintenance.  
* A post from iass-potsdam states that "An additional aspect of local value creation is linked to the emergence of citizens as renewable energy producers and energy providers. An estimated 47% of the overall installed renewable energy capacity in Germany as of 2013 — adding up to an installed capacity of 33.5 GW — is in the hand of citizens, mainly through privately owned solar rooftop systems and citizens’ wind farm cooperatives. Those projects provide approximately 1.6 million Germans with additional income or reduced spending for external electricity."

Reference:
<https://en.wikipedia.org/wiki/Renewable_energy_in_Germany>

<https://www.cleanenergywire.org/news/renewables-hit-record-77-percent-german-power-easter-monday>

<https://www.iass-potsdam.de/en/blog/2016/10/social-benefits-renewable-energies>

## E.Datacenter.8
**Google Cloud Data Center Outage**

* Google Cloud Data Center encountered an outage on June 2nd 2019 12.53 PST. This outage caused slow performance and increased error rates on several Google services, including Google Cloud Platform, YouTube, Gmail, Google Drive and others.  
* Google Cloud status mentions that "Multiple US regions noticed a elevated packet loss due to a network congestion for duration between 3 hours 19 minutes - 4 hours 25minutes."
* The cause was found to be due to an incorrect configuration change that was applied to a larger number of servers in several regions but originally intended for small group of servers in a single region. Due to this, the impacted regions were running 50% of their available network capacity.
* The impacted regions were "us-central1, us-east1, us-east4, us-west2, northamerica-northeast1, and southamerica-east1." 
* From a user impact perspective, Google Cloud's blog states that "YouTube measured a 2.5% drop of views for one hour, while Google Cloud Storage measured a 30% reduction in traffic." Around 1% of active Gmail users, which would represent a million users couldn't send or receive emails.
* Services that were impacted include Cloud Endpoint, Cloud Interconnect, Cloud VPN, Cloud Pub /Sub, Cloud Spanner and Cloud Storage.

Reference:
 <https://status.cloud.google.com/incident/cloud-networking/19009> 

<https://cloud.google.com/blog/topics/inside-google-cloud/an-update-on-sundays-service-disruption> 
