import React from 'react'

function Hazards() {
  return (
    <div className='h-[100vh] overflow-y-hidden'>
        <div className='overflow-y-auto max-h-1/2' style={{ maxHeight: 'calc(100% - 50vh)' }}>
            <h3 className='text-2xl bg-orange-200 p-2 text-center rounded'>Data Hazards</h3>
            <div>
                Lorem, ipsum dolor sit amet consectetur adipisicing elit. Ad recusandae obcaecati, fuga ullam non quia dolores in dolorem, veniam aliquid tenetur quae, sequi deserunt et voluptatum velit consequatur provident consequuntur.
                Lorem ipsum, dolor sit amet consectetur adipisicing elit. Labore doloremque quo dolores expedita voluptate voluptatibus aperiam, reprehenderit voluptates ab asperiores in nostrum tempora, sequi, iste cupiditate commodi distinctio! Cum, delectus.
            </div>
        </div>
        <div className='overflow-y-auto max-h-1/2' style={{ maxHeight: 'calc(100% - 50vh)' }}>
            <h3 className='text-2xl bg-orange-200 p-2 text-center rounded'>Control Hazards</h3>
            <div>
                Lorem, ipsum dolor sit amet consectetur adipisicing elit. Repellat nam, autem fugit harum doloremque officia, aperiam voluptas sint reprehenderit ipsam odio velit eligendi similique eveniet tempore debitis ab voluptatibus ipsum.
                Lorem ipsum dolor sit amet consectetur adipisicing elit. Aut, asperiores cumque, distinctio laudantium a at optio obcaecati temporibus, beatae unde quod amet repudiandae? Voluptatem necessitatibus harum, libero corrupti accusamus quisquam nostrum consequatur et nesciunt ipsum magnam sapiente eum, at perferendis!
            </div>
        </div>
    </div>
  )
}

export default Hazards