import streamlit as st


def main() -> None:
    st.set_page_config(page_title="PlanMyBerlin", page_icon="🗺️")

    st.title("PlanMyBerlin – Berlin Trip Planner")
    st.caption("Sprint 2 – Building Applications with LangChain, RAGs, and Streamlit")

    st.markdown(
        """
        Welcome to **PlanMyBerlin**.

        This app will help visitors plan realistic day-by-day trips to Berlin,
        tailored to their interests, budget, and time.

        For now, this is a minimal homepage to confirm the setup works.
        The itinerary planning, RAG knowledge base, and tools will be added next.
        """
    )


if __name__ == "__main__":
    main()

