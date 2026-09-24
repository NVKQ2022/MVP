using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Domain.Common.Interfaces
{
    public interface IActivatable
    {
        bool IsActive { get; }

        void Activate();

        void Deactivate();
    }
}
