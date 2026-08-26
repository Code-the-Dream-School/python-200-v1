# Introduction to Cloud Computing

Over the past seven weeks you've built machine learning models, worked with data pipelines, and built AI tools -- all on your local machine.

This week you'll start learning about **cloud computing**, which is where a lot of that work happens in practice in industry. This lesson gives you the conceptual foundation: what the cloud is, why it exists, and how it's organized.

Think back to the last time a major app went down -- Netflix on a holiday weekend, or your bank's website on a busy shopping day. These outages make headlines partly because they're rare, and they're rare because large services run on infrastructure designed to scale and recover automatically: the cloud. The cloud has become the default environment for building and running data-intensive software, and understanding why is a good place to start.

The core idea is simple: instead of buying and maintaining your own computing resources, you rent resources from a provider -- storage, processing power, networking -- and pay for what you use. Need to train a machine learning model that would melt your laptop? Rent a GPU cluster for an afternoon, then shut it down. Need to store a terabyte of data? No hard drives required. This *pay-as-you-go model*, combined with virtually unlimited scale, is what makes cloud computing so powerful.

As you get started, these two videos are a great starting point for learning about cloud:

1. ["Cloud Computing Basics," from CodeBagel.](https://youtu.be/N0SYCyS2xZA?si=33wKRGxjzfEvhX3z) This is a brief (2 minute) video explaining what cloud computing is and why developers use the cloud.
2. ["Cloud Computing Explained," from Be A Better Dev](https://youtu.be/ZaA0kNm18pE?si=cUM1ISwuScq40Vih). This longer video (45 minutes) is a more in-depth breakdown of how cloud computing actually works and introduces you to some key concepts we'll discuss in these lessons.

## Learning Objectives

By the end of this lesson, you will be able to:

* Explain what cloud computing is and why it matters
* Describe the main benefits cloud infrastructure provides
* Distinguish between IaaS, PaaS, and SaaS
* Understand the tradeoffs between cloud providers and managed data platforms

## What is Cloud Computing?

Cloud computing means renting computing infrastructure from a provider rather than owning it. The three dominant providers -- Amazon Web Services (AWS), Google Cloud Platform (GCP), and Microsoft Azure -- each operate a global network of data centers: physical facilities packed with servers, storage hardware, and networking equipment. When you spin up a virtual machine or upload a file to cloud storage, you're using hardware in one of these facilities, somewhere in the world. Providers organize their infrastructure into *regions* -- named geographic locations like “US East” or “West Europe” -- and you'll choose a region whenever you create a cloud resource.

All three providers offer largely the same catalog of services, just under different names. The diagram below maps equivalent services across AWS, GCP, and Azure. No need to memorize the diagram, just notice that the categories are consistent: storage, compute, databases, networking, machine learning, and so on.

![Cloud Services Overview](resources/cloud_services_overview.png)

### What Cloud Does Well

So why have so many industry services moved to the cloud? A few properties stand out.

*Scalability* is the headline benefit. Cloud infrastructure can grow (or shrink) with your workload in ways that physical hardware simply can't. There are two flavors: *vertical scaling* means upgrading the machine itself -- more CPU, more RAM, a bigger GPU -- while *horizontal scaling* means adding more machines and splitting the work across them. The latter is how large services handle unpredictable demand: when traffic spikes, the cloud provisions additional instances automatically and winds them back down when things quiet. You pay for what you use, not for peak capacity sitting idle most of the time.

A simple mental model:

* *Vertical scaling* = making one machine bigger (more RAM, CPU, GPU)
* *Horizontal scaling* = adding more machines and splitting the work across them

You’ll see both patterns constantly in cloud environments.

*Reliability* is the other major draw. Cloud providers operate redundant data centers and typically guarantee uptime above 99.9%. For a pipeline that needs to run on a schedule or a service that needs to be reachable around the clock, that reliability is hard to replicate on your own hardware.

Beyond those two, cloud infrastructure offers things that are harder to quantify but genuinely matter: you can spin up a new environment in minutes rather than waiting weeks for hardware to arrive and be configured; you can go global by simply choosing a different region; and you offload the maintenance burden -- security patches, hardware failures, capacity planning -- to the provider. AWS has a useful [summary of the advantages of cloud computing](https://aws.amazon.com/what-is-cloud-computing/) if you want a more complete picture.

### How Cloud Services Are Delivered

Cloud services exist on a spectrum defined by a simple question: *how much does the provider manage for you?*

At one end, you get raw computing resources -- a virtual machine, some storage, a network connection -- and you set up everything yourself, just as you would on your own computer. You choose the operating system, install your software, configure your environment, and handle security updates. This is called *Infrastructure as a Service (IaaS)*. It's the most flexible option, but also the most work. Examples: AWS EC2, Google Compute Engine, Azure Virtual Machines.

At the other end, you open a browser and use an application someone else built, runs, and maintains. You don't think about servers at all. That's *Software as a Service (SaaS)* -- Gmail, Dropbox, and Google Docs are everyday examples. You just log in and use them; someone else handles the rest.

In between sits *Platform as a Service (PaaS)*: the provider manages the infrastructure, but you bring your own code. You deploy an application or a script, and the platform handles running it, scaling it, and keeping the underlying machine healthy. Examples: Azure App Service, AWS Elastic Beanstalk, Google App Engine.

The key question for each level is just: “what do I have to manage?” With IaaS, everything from the OS up. With PaaS, your code and configuration. With SaaS, almost nothing.

**Check out [this CertBros video](https://youtu.be/lex-DYi1UpU?si=Xa-bg-y0UldTI53K&t=395) for a review of IaaS, PaaS, and SaaS (start at 6:35 if you want to skip the review of cloud basics).**

### Limitations and Costs

The cloud isn't the right tool for every problem.

If your dataset fits comfortably on a single machine and you do not have massive compute demands, local processing is often faster and cheaper. This is often the best approach when setting up an initial prototype.

The learning curve for cloud infrastructure can be very steep. Even doing simple things in the cloud can take a long time, as you have to figure out the right resources and jargon initially.

It is completely normal for cloud platforms to feel overwhelming at first. Azure, AWS, and GCP are enormous ecosystems with hundreds of services, and even experienced engineers regularly look things up while working.

Getting support is not as easy as with common Python packages like Matplotlib, so there can be delays if you need help. While AI can be extremely helpful for explaining cloud concepts, cloud platforms are notorious for how fast they change, so just beware that AI models will not always give you the most up-to-date advice.

Be prepared to be patient, and to learn a new style of "programming" in the coming weeks. We put "programming" in quotes because cloud computing is not just about writing code, it's about finding the right levers in a large ecosystem of resources to get the job done. If your internet provider or cloud provider goes down, you may need to take a break.

Finally, while cloud advocates will often say the cloud is cheap (because you only pay for what you use), cloud costs can spiral fast if you're not careful. Leaving a GPU cluster running overnight or forgetting to clean up storage can generate surprising bills. That said, you can easily set up guardrails and cost alerts to minimize the chances of such things happening.

## Cloud Providers vs Managed Data Platforms

In practice, you'll encounter two distinct flavors of cloud infrastructure: the major cloud providers themselves (AWS, GCP, Azure), and a layer of *managed data platforms* built on top of them -- primarily Databricks, Snowflake, and Dataiku.

Cloud providers give you the full toolkit: compute, storage, networking, machine learning services, databases, and dozens of other services. They're highly flexible but require significant configuration. You're assembling your own stack from pieces, which gives you control but takes time and expertise to set up well.

Managed data platforms take a different approach: they pre-wire the pieces for you, optimizing specifically for data and analytics workloads. Databricks, for example, runs on top of AWS, GCP, or Azure -- it's not a separate cloud, it's a curated layer that provisions and manages cloud resources on your behalf. This makes it much faster to get started with large-scale data processing or machine learning, at the cost of some flexibility and, potentially higher costs.

## Wrap-up

Before diving into the hands-on Azure work in the next lesson, take some time to work through Microsoft's learning module on cloud fundamentals. It will reinforce what you've read here and fill in any gaps.

* [Introduction to Microsoft Azure: Describe Cloud Concepts](https://learn.microsoft.com/en-us/training/paths/microsoft-azure-fundamentals-describe-cloud-concepts/)
