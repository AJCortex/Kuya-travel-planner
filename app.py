import streamlit as st
import os
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.serpapi_tools import SerpApiTools

# Initialize page config
st.set_page_config(
    page_title="Kuya Globe",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS for improved UI
st.markdown("""
    <style>
    :root {
        --primary-color: #2E86C1;
        --accent-color: #FF6B6B;
        --background-light: #F8F9FA;
        --text-color: #2C3E50;
        --hover-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .main {
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }

    .stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: var(--accent-color) !important;
        color: white !important;
        font-weight: bold;
        font-size: 1rem;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--hover-shadow);
        background-color: #FF4A4A !important;
    }

    .sidebar .element-container {
        background-color: var(--background-light);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .stExpander {
        background-color: #262730;
        border-radius: 10px;
        padding: 1rem;
        border: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .travel-summary {
        background-color: #262730;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }

    .travel-summary h4 {
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }

    .agent-header {
        background-color: #1a1c24;
        border-left: 4px solid var(--primary-color);
        padding: 0.75rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 1rem;
        font-weight: bold;
        font-size: 1rem;
    }

    .spinner-text {
        font-size: 1.2rem;
        font-weight: bold;
        color: var(--primary-color);
    }

    </style>
""", unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/airplane-take-off.png")
    st.title("Trip Settings")
    
    # User inputs for API keys
    groq_api_key = st.text_input("🔑 Enter your Groq API Key", type="password")
    serpapi_key = st.text_input("🔑 Enter your SerpAPI Key", type="password")
    
    destination = st.text_input("🌍 Where would you like to go?", "")
    duration = st.number_input("📅 How many days?", min_value=1, max_value=30, value=5)
    
    budget = st.select_slider(
        "💰 What's your budget level?",
        options=["Budget", "Moderate", "Luxury"],
        value="Moderate"
    )
    
    travel_style = st.multiselect(
        "🎯 Travel Style",
        ["Culture", "Nature", "Adventure", "Relaxation", "Food", "Shopping"],
        ["Culture", "Nature"]
    )

# Initialize session state variables
if 'travel_plan' not in st.session_state:
    st.session_state.travel_plan = None
if 'qa_expanded' not in st.session_state:
    st.session_state.qa_expanded = False

# Add loading state container
loading_container = st.empty()

try:
    # Set API keys in environment variables
    os.environ["GROQ_API_KEY"] = groq_api_key
    os.environ["SERP_API_KEY"] = serpapi_key

    # ── Agent 1: Travel Planner ──────────────────────────────────────────────
    travel_agent = Agent(
        name="Travel Planner",
        model=Groq(id="llama-3.3-70b-versatile"),
        tools=[SerpApiTools()],
        instructions=[
            "You are a travel planning assistant.",
            "Help users plan their trips by researching destinations, finding attractions, suggesting accommodations, and providing transportation options.",
            "Give relevant live links for each place and hotel you recommend by searching the internet.",
            "Always verify information is current before making recommendations.",
            "Format your response in clear markdown with headings and bullet points."
        ],
        show_tool_calls=True,
        markdown=True
    )

    # ── Agent 2: Local Expert ────────────────────────────────────────────────
    local_expert_agent = Agent(
        name="Local Expert",
        model=Groq(id="llama-3.3-70b-versatile"),
        instructions=[
            "You are a knowledgeable local guide with deep understanding of the destination's culture and attractions.",
            "Provide detailed insights about the destination including hidden gems, off-the-beaten-path experiences, and local customs.",
            "Share insider tips that most tourists never discover.",
            "Include cultural etiquette, local phrases, neighborhood breakdowns, and authentic local food spots.",
            "Draw on your extensive knowledge to provide accurate and helpful local information.",
            "Format your response in clear markdown with headings and bullet points."
        ],
        show_tool_calls=False,
        markdown=True
    )

    # ── Agent 3: Logistics Coordinator ──────────────────────────────────────
    logistics_agent = Agent(
        name="Logistics Coordinator",
        model=Groq(id="llama-3.3-70b-versatile"),
        instructions=[
            "You are an experienced travel logistics specialist who ensures smooth and efficient travel planning.",
            "Plan and optimize travel arrangements including accommodations, transportation, and scheduling.",
            "Recommend the best booking platforms, transit options, and practical travel tools.",
            "Provide estimated costs, booking tips, and contingency advice.",
            "Draw on your extensive knowledge to provide accurate logistics recommendations.",
            "Format your response in clear markdown with headings and bullet points."
        ],
        show_tool_calls=False,
        markdown=True
    )

    # Main UI
    st.title("🌎 Kuya Globe Travel Planner")
    
    st.markdown(f"""
        <div class="travel-summary">
            <h4>Welcome to your personal AI Travel Assistant! 🌟</h4>
            <p>Three specialized agents will collaborate sequentially to build your perfect trip.</p>
            <p><strong>Destination:</strong> {destination}</p>
            <p><strong>Duration:</strong> {duration} days</p>
            <p><strong>Budget:</strong> {budget}</p>
            <p><strong>Travel Styles:</strong> {', '.join(travel_style)}</p>
        </div>
    """, unsafe_allow_html=True)

    # Generate button
    if st.button("✨ Generate My Perfect Travel Plan", type="primary"):
        if destination:
            try:
                travel_styles_str = ', '.join(travel_style)

                # ── Step 1: Travel Planner ───────────────────────────────────
                st.markdown('<div class="agent-header">🗺️ Step 1 of 3 — Travel Planner is building your itinerary...</div>', unsafe_allow_html=True)
                with st.spinner("Researching destinations and drafting your itinerary..."):
                    planner_prompt = f"""Create a comprehensive travel plan for {destination} for {duration} days.

Travel Preferences:
- Budget Level: {budget}
- Travel Styles: {travel_styles_str}

Please provide a detailed itinerary that includes:

1. 🌞 Best Time to Visit
   - Seasonal highlights
   - Weather considerations

2. 🏨 Accommodation Recommendations
   - {budget} range hotels/stays
   - Locations and proximity to attractions

3. 🗺️ Day-by-Day Itinerary
   - Detailed daily activities
   - Must-visit attractions
   - Local experiences aligned with travel styles

4. 🍽️ Culinary Experiences
   - Local cuisine highlights
   - Recommended restaurants
   - Food experiences matching travel style

5. 💰 Estimated Total Trip Cost
   - Breakdown of expenses
   - Money-saving tips

Please provide source and relevant links. Format in clear markdown with headings and bullet points.
"""
                    planner_response = travel_agent.run(planner_prompt)
                    planner_output = planner_response.content if hasattr(planner_response, 'content') else str(planner_response)
                    planner_output = planner_output.replace('∣', '|').replace('\n\n\n', '\n\n')

                with st.expander("🗺️ Travel Planner Results", expanded=True):
                    st.markdown(planner_output)

                # ── Step 2: Local Expert ─────────────────────────────────────
                st.markdown('<div class="agent-header">🧭 Step 2 of 3 — Local Expert is uncovering hidden gems and local insights...</div>', unsafe_allow_html=True)
                with st.spinner("Gathering local knowledge and insider tips..."):
                    local_prompt = f"""Based on this travel plan for {destination}:

{planner_output}

Now provide detailed local insights including:

1. 🏘️ Neighborhood Guide
   - Best areas to stay and explore by travel style
   - What each neighborhood is known for

2. 💎 Hidden Gems
   - Off-the-beaten-path attractions most tourists miss
   - Secret spots and local favorites

3. 🎭 Local Customs and Culture
   - Cultural etiquette and do's and don'ts
   - Local phrases and language tips
   - Dress codes and social norms

4. 🍜 Authentic Local Food Scene
   - Where locals actually eat (not tourist traps)
   - Must-try street food and markets
   - Food customs and dining etiquette

5. 📅 Local Events and Seasonal Highlights
   - Festivals, markets, or events during the travel period
   - Best times of day to visit popular spots to avoid crowds

Please provide relevant links. Format in clear markdown with headings and bullet points.
"""
                    local_response = local_expert_agent.run(local_prompt)
                    local_output = local_response.content if hasattr(local_response, 'content') else str(local_response)
                    local_output = local_output.replace('∣', '|').replace('\n\n\n', '\n\n')

                with st.expander("🧭 Local Expert Insights", expanded=True):
                    st.markdown(local_output)

                # ── Step 3: Logistics Coordinator ────────────────────────────
                st.markdown('<div class="agent-header">✈️ Step 3 of 3 — Logistics Coordinator is optimizing your travel arrangements...</div>', unsafe_allow_html=True)
                with st.spinner("Planning transportation, bookings, and logistics..."):
                    logistics_prompt = f"""Based on this travel plan and local insights for {destination} ({duration} days, {budget} budget):

TRAVEL PLAN:
{planner_output}

LOCAL INSIGHTS:
{local_output}

Now provide a complete logistics plan including:

1. ✈️ Getting There
   - Best flight routes and airlines for {budget} budget
   - Airport transfer options and costs
   - Booking platforms and best time to book

2. 🚌 Getting Around
   - Local transportation options (metro, bus, taxi, rideshare)
   - Day trip logistics from the city
   - Transportation passes or cards worth buying

3. 🏨 Accommodation Booking Strategy
   - Best booking platforms for {budget} budget
   - Recommended neighborhoods to stay based on the itinerary
   - Check-in/check-out logistics and luggage storage tips

4. 📋 Day-by-Day Logistics Optimization
   - Optimized order of attractions to minimize travel time
   - Opening hours and reservation requirements
   - Pre-booking recommendations

5. 📱 Essential Apps and Tools
   - Must-have apps for navigation, translation, and booking
   - Offline tools for areas with limited connectivity

6. 🔗 Booking Links and Resources
   - Direct links to recommended booking platforms
   - Estimated total logistics cost breakdown

Format in clear markdown with headings and bullet points.
"""
                    logistics_response = logistics_agent.run(logistics_prompt)
                    logistics_output = logistics_response.content if hasattr(logistics_response, 'content') else str(logistics_response)
                    logistics_output = logistics_output.replace('∣', '|').replace('\n\n\n', '\n\n')

                with st.expander("✈️ Logistics Plan", expanded=True):
                    st.markdown(logistics_output)

                # ── Combine all outputs into session state ───────────────────
                full_plan = f"""# Your Complete Travel Plan for {destination}

## 🗺️ Itinerary
{planner_output}

## 🧭 Local Expert Insights
{local_output}

## ✈️ Logistics Plan
{logistics_output}
"""
                st.session_state.travel_plan = full_plan
                st.success("✅ Your complete travel plan is ready!")

            except Exception as e:
                st.error(f"Error generating travel plan: {str(e)}")
                st.info("Please try again in a few moments.")
        else:
            st.warning("Please enter a destination")

    # Q&A Section
    st.divider()
    
    qa_expander = st.expander("🤔 Ask a specific question about your destination or travel plan", expanded=st.session_state.qa_expanded)
    
    with qa_expander:
        st.session_state.qa_expanded = True
        
        question = st.text_input("Your question:", placeholder="What would you like to know about your trip?")
        
        if st.button("Get Answer", key="qa_button"):
            if question and st.session_state.travel_plan:
                with st.spinner("🔍 Finding answer..."):
                    try:
                        context_question = f"""
I have a travel plan for {destination}. Here's the existing plan:
{st.session_state.travel_plan}

Now, please answer this specific question: {question}

Provide a focused, concise answer that relates to the existing travel plan if possible.
"""
                        response = travel_agent.run(context_question)
                        if hasattr(response, 'content'):
                            st.markdown(response.content)
                        else:
                            st.markdown(str(response))
                    except Exception as e:
                        st.error(f"Error getting answer: {str(e)}")
            elif not st.session_state.travel_plan:
                st.warning("Please generate a travel plan first before asking questions.")
            else:
                st.warning("Please enter a question")

except Exception as e:
    st.error(f"Application Error: {str(e)}")
